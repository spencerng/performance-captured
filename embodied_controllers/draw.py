import cv2 as cv
import pygame as pg
import statistics

import os
import csv
import math

from kinect import KinectCam
from snes import Emulator, Game
from config import *

# Remember to run with sudo


def cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    return pg.image.frombuffer(image.tostring(), image.shape[1::-1], "BGR")


GAMES = [
    Game(
        "roms/super_mario_all_stars_usa.sfc",
        pg.Color(227, 0, 42),
        pg.Color(0, 227, 23),
        "backgrounds/mario_img.jpg",
        save_state=0,
        action_key="s",
        jump_key="x",
        action_thresh=ACTION_THRESH,
        move_thresh=MOVE_THRESH,
    )
]


def main():
    pg.display.init()
    pg.font.init()
    pg.display.set_caption("Embodied Play")

    retro_font = pg.font.SysFont("retrogaming", 48)
    screen = pg.display.set_mode(RES, pg.RESIZABLE)
    clock = pg.time.Clock()

    cam = KinectCam()
    emu = Emulator(GAMES)

    running = True
    started = False
    t = 0

    centroid_window = list()

    

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        cv_img, centroids, player_contour, flow_props = cam.get_frame()

        if not started and player_contour is None:
            text = retro_font.render("ENTER SPACE TO BEGIN", True, (255, 255, 255))
            text_rect = text.get_rect(center=(RES[0] / 2, RES[1] / 2))
            screen.blit(text, text_rect)

        elif cv_img is not None:
            if not started:
                started = True
                left_color, right_color, bg_source = emu.rotate_game()
                background = pg.transform.scale(
                    pg.image.load(bg_source), (RES[0], RES[1])
                )

            screen.blit(background, (0, 0))

            if len(centroids) == 0:
                emu.controller.clear_inputs()
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

                emu.controller.process_input(x_med, y_med, flow_props)
                _, jumping, action = emu.controller.press_buttons()

                right_percent = max(0, min(1, (x_med - X_LEFT_THRESH) / (X_WINDOW * 2)))

                player_color = left_color.lerp(right_color, right_percent)

                # TODO: Add jump/action status text here
                # player_color.a = 255 if jumping else 50

            if player_contour is not None:
                pg.draw.polygon(screen, player_color, player_contour)
                pg.draw.circle(screen, (255, 0, 0), (x_med, y_med), 30)

        pg.display.update()

        # Limit FPS
        clock.tick(30)

    cam.close()
    # controller.log.close()


if __name__ == "__main__":
    main()
