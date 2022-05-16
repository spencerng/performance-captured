import cv2 as cv
import pygame as pg
from kinect import KinectCam

# Remember to run with sudo
def cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    return pg.image.frombuffer(image.tostring(), image.shape[1::-1], "BGR")


def main():
    pg.init()
    screen = pg.display.set_mode((1920, 1080))
    clock = pg.time.Clock()
    cam = KinectCam()
    running = True
    t = 0
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        frame_info = cam.get_frame()

        if frame_info is not None:
            cv_img, centroids = frame_info
            screen.blit(cvimage_to_pygame(cv_img), (0, 0))
            for centroid in centroids:
                # print(type(surface))
                pg.draw.circle(screen, (255, 0, 0), centroid, 30)

            pg.display.update()

        # Limit FPS
        clock.tick(30)

    cam.close()


if __name__ == "__main__":
    main()
