import cv2 as cv
import pygame as pg
import statistics
import keyboard

from kinect import KinectCam

# Remember to run with sudo
def cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    return pg.image.frombuffer(image.tostring(), image.shape[1::-1], "BGR")


X_WINDOW = 175
X_LEFT_THRESH = 1920 / 2 - X_WINDOW
X_RIGHT_THRESH = 1920 / 2 + X_WINDOW
WINDOW_SIZE = 5

JUMP_THRESH = 50


class Controller:
    def __init__(self):
        self.side_button_press = None
        self.a_state = False
        self.prev_y = None
        self.jump_count = 0

    def process_input(self, x_pos, y_pos):
        if x_pos > X_RIGHT_THRESH:
            self.side_button_press = "RIGHT"
        elif x_pos < X_LEFT_THRESH:
            self.side_button_press = "LEFT"
        else:
            self.side_button_press = None

        if self.prev_y is not None:
            if y_pos < self.prev_y and abs(self.prev_y - y_pos) > JUMP_THRESH:
                self.a_state = True
                self.jump_count += 1
            elif y_pos > self.prev_y and abs(self.prev_y - y_pos) > JUMP_THRESH:
                self.a_state = False
                self.jump_count = 0

        self.prev_y = y_pos

    def press_buttons(self):
        if self.side_button_press == "RIGHT":
            keyboard.press("right")
        elif self.side_button_press == "LEFT":
            keyboard.press("left")
        else:
            keyboard.release("left")
            keyboard.release("right")

        if self.a_state and self.jump_count < 20:
            keyboard.press("x")
        else:
            keyboard.release("x")


def main():
    pg.display.init()
    pg.font.init()
    screen = pg.display.set_mode((1920, 1080))
    clock = pg.time.Clock()
    cam = KinectCam()

    controller = Controller()

    running = True
    t = 0

    centroid_window = list()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        frame_info = cam.get_frame()

        if frame_info is not None:
            cv_img, centroids = frame_info
            screen.blit(cvimage_to_pygame(cv_img), (0, 0))

            pg.draw.line(screen, (0, 255, 0), (X_LEFT_THRESH, 0), (X_LEFT_THRESH, 1080))
            pg.draw.line(
                screen, (0, 128, 128), (X_RIGHT_THRESH, 0), (X_RIGHT_THRESH, 1080)
            )

            if len(centroids) == 0:
                if len(centroid_window) != 0:
                    centroid_window.pop(0)
            else:
                centroid = centroids[0]
                centroid_window.append(centroid)

                if len(centroid_window) > WINDOW_SIZE:
                    centroid_window.pop(0)

            if len(centroid_window) != 0:
                x_med = statistics.median(map(lambda x: x[0], centroid_window))
                y_med = statistics.median(map(lambda x: x[1], centroid_window))

                pg.draw.circle(screen, (255, 0, 0), (x_med, y_med), 30)
                controller.process_input(x_med, y_med)

            pg.display.update()

        controller.press_buttons()
        # Limit FPS
        clock.tick(30)

    cam.close()


if __name__ == "__main__":
    main()
