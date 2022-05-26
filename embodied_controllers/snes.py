import keyboard
import subprocess as sp
from threading import Thread
import math
import statistics
from config import *


class Controller:
    def __init__(self):
        self.side_button_press = None
        self.down_held = False
        self.a_state = False
        self.action_state = False
        self.prev_y = None
        self.jump_count = 0
        self.game = None

        self.motion_window = list()
        self.x_motion_window = list()
        # self.log = open("log.csv", "w+")
        # self.writer = csv.DictWriter(self.log, ['mean_y', 'mean_x', 'motion_point_x', 'motion_point_y'])

    def process_input(self, x_pos, y_pos, flow_props):
        if self.game is None:
            return

        if y_pos > CROUCH_Y_THRESH:
            self.down_held = True
            self.side_button_press = None
            self.a_state = False
            self.action_state = False
            return

        self.down_held = False

        # self.writer.writerow(flow_props)

        vel = math.sqrt(flow_props["mean_x"] ** 2 + flow_props["mean_y"] ** 2)

        self.x_motion_window.append(flow_props["mean_x"])
        self.motion_window.append(vel)

        if len(self.motion_window) > 3:
            self.motion_window.pop(0)
        if len(self.x_motion_window) > 3:
            self.x_motion_window.pop(0)

        if statistics.mean(self.x_motion_window) >= self.game.action_thresh:
            self.action_state = True
        else:
            self.action_state = False

        if statistics.median(self.motion_window) >= self.game.move_thresh:
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
            keyboard.press(self.game.jump_key)
        else:
            keyboard.release(self.game.jump_key)

        if self.action_state:
            keyboard.press(self.game.action_key)

        else:
            keyboard.release(self.game.action_key)

        return self.side_button_press, self.a_state

    def clear_inputs(self):
        self.side_button_press = None
        self.a_state = False
        self.action_state = False

        keyboard.release("left")
        keyboard.release("right")
        keyboard.release(self.game.jump_key)
        keyboard.release(self.game.action_key)

    def change_controls(self, game):
        self.game = game


class Game:
    def __init__(
        self,
        path,
        left_color,
        right_color,
        background_img,
        save_state=0,
        action_key=ACTION_KEY,
        jump_key=JUMP_KEY,
        action_thresh=ACTION_THRESH,
        move_thresh=MOVE_THRESH,
    ):
        self.path = path
        self.save_state = save_state
        self.action_key = action_key
        self.jump_key = jump_key
        self.action_thresh = action_thresh
        self.move_thresh = move_thresh
        self.left_color = left_color
        self.right_color = right_color
        self.background = background_img

class Emulator:
    def __init__(self, games):
        self.process = None
        self.controller = Controller()
        self.index = 0
        self.games = games

    def rotate_game(self):
        game = self.games[self.index]
        self.index = (self.index + 1) % len(self.games)
        
        return game.left_color, game.right_color, game.background

    def start_game(self, game):
        if self.process is not None:
            self.process.kill()

        self.controller.change_controls(game)

        def target(**kwargs):
            self.process = sp.run(f"zsnes -zs {game.save_state} {game.path}".split(" "))

        thread = Thread(target=target)
        thread.start()

        
