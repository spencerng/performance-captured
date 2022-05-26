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
        "backgrounds/smb_background.png",
        save_state=0,
        action_key="s",
        jump_key="x",
        action_thresh=ACTION_THRESH,
        move_thresh=MOVE_THRESH,
    ),
    Game(
        "roms/super_mario_world.sfc",
        pg.Color(255, 57, 57),
        pg.Color(0, 206, 0),
        "backgrounds/super_mario_world.png",
        save_state=0,
        action_key="a",
        jump_key="z",
        action_thresh=0.0015,
        move_thresh=0.0010,
    ),
    Game(
        "roms/super_street_fighter.sfc",
        pg.Color(255, 255, 255),
        pg.Color(242, 103, 44),
        "backgrounds/street_fighter.png",
        save_state=0,
        action_key="s",
        jump_key="up",
        action_thresh=0.0010,
        move_thresh=0.0005,
    ),
    Game(
        "roms/kirby_super_star.sfc",
        pg.Color(235, 104, 150),
        pg.Color(253, 153, 167),
        "backgrounds/kirby_super_star.png",
        save_state=0,
        action_key="a",
        jump_key="z",
        action_thresh=0.0010,
        move_thresh=0.0005,
    ),
    Game(
        "roms/super_mario_kart.sfc",
        pg.Color(4, 156, 216),
        pg.Color(251, 208, 0),
        "backgrounds/super_mario_kart.png",
        save_state=0,
        action_key="z",
        jump_key="x",
        action_thresh=0.000,
        move_thresh=0.0000,
    ),
    Game(
        "roms/super_punch_out.sfc",
        pg.Color(255, 36, 0),
        pg.Color(255, 0, 255),
        "backgrounds/punch_out.png",
        save_state=0,
        action_key="z",
        jump_key="up",
        action_thresh=0.0015,
        move_thresh=0.0010,
    ),
    Game(
        "roms/super_mario_all_stars_usa.sfc",
        pg.Color(227, 0, 42),
        pg.Color(0, 227, 23),
        "backgrounds/super_mario_bros_uground.png",
        save_state=1,
        action_key="s",
        jump_key="x",
        action_thresh=0.0015,
        move_thresh=MOVE_THRESH,
    ),
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

    game_running_timer = 0

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
            if not started or game_running_timer > 30 * SECONDS_PER_GAME:
                started = True

                game_running_timer = 0
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
                # pg.draw.circle(screen, (255, 0, 0), (x_med, y_med), 30)

        game_running_timer += 1
        pg.display.update()

        # Limit FPS
        clock.tick(30)

    cam.close()
    # controller.log.close()


if __name__ == "__main__":
    main()
