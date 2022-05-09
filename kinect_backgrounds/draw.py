import cv2 as cv
import pygame as pg
from kinect import KinectCam

# Remember to run with sudo
def cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    return pg.image.frombuffer(image.tostring(), image.shape[1::-1],
                                   "BGR")

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

        cv_img = cam.get_frame()
        if cv_img is not None:
            screen.blit(cvimage_to_pygame(cv_img), (0,0))

            pg.display.update()

        # Limit FPS
        clock.tick(30)

    cam.close()
     
if __name__=="__main__":
    main()