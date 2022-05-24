import cv2 as cv
import pygame as pg
import statistics
import keyboard

from kinect import KinectCam

# Remember to run with sudo

SCALE = 1/1.5

RES = list(map(int, (1920 * SCALE, 1080 * SCALE)))

X_WINDOW = 160 * SCALE
X_LEFT_THRESH = (1920 / 2 - X_WINDOW) * SCALE
X_RIGHT_THRESH = (1920 / 2 + X_WINDOW) * SCALE
WINDOW_SIZE = 5

# Minimum centroid position for a crouch position
CROUCH_Y_THRESH = 800 * SCALE

# Threshold in pixels for one keypress of jumping
JUMP_THRESH = 100 * SCALE
JUMP_KEY = "z" # x for other game


def cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    return pg.image.frombuffer(image.tostring(), image.shape[1::-1], "BGR")


class Controller:
    def __init__(self):
        self.side_button_press = None
        self.down_held = False
        self.a_state = False
        self.prev_y = None
        self.jump_count = 0

    def process_input(self, x_pos, y_pos):
        if y_pos > CROUCH_Y_THRESH:
            self.down_held = True
            self.side_button_press = None
            self.a_state = False
            return

        self.down_held = False

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
        if self.down_held:
            keyboard.press("down")
        else:
            keyboard.release("down")

        if self.side_button_press == "RIGHT":
            keyboard.press("right")
        elif self.side_button_press == "LEFT":
            keyboard.press("left")
        else:
            keyboard.release("left")
            keyboard.release("right")

        if self.a_state and self.jump_count < 20:
            keyboard.press(JUMP_KEY)
        else:
            keyboard.release(JUMP_KEY)

        return self.side_button_press, self.a_state



def main():
    pg.display.init()
    pg.font.init()
    screen = pg.display.set_mode(RES)
    clock = pg.time.Clock()
    cam = KinectCam()

    controller = Controller()

    running = True
    started = False
    t = 0

    centroid_window = list()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        frame_info = cam.get_frame()

        if not started:
            # Draw starting screen here
            pass


        if frame_info is not None:
            if not started:
                started = True
                # TODO: Launch command here
                cmd = "zsnes -zs 0 ~/Downloads/Super\\ Mario\\ All-Stars\\ \\(USA\\).sfc"



            cv_img, centroids, player_contour = frame_info
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

                controller.process_input(x_med, y_med)

                _, jumping = controller.press_buttons()

                right_color = pg.Color(0, 227, 23)
                left_color = pg.Color(227, 0, 42)
                right_percent = max(0, min(1, (x_med - X_LEFT_THRESH) / (X_WINDOW * 2)))

                player_color = left_color.lerp(right_color, right_percent)


                player_color.a = 255 if jumping else 50

            if player_contour is not None:
                pg.draw.polygon(screen, player_color, player_contour)
                pg.draw.circle(screen, (255, 0, 0), (x_med, y_med), 30)

            pg.display.update()

        # Limit FPS
        clock.tick(30)

    cam.close()


if __name__ == "__main__":
    main()
