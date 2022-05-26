SCALE = 1 / 1.5

RES = list(map(int, (1920 * SCALE, 1080 * SCALE)))

X_WINDOW = 160 * SCALE
X_LEFT_THRESH = (1920 / 2 - X_WINDOW) * SCALE
X_RIGHT_THRESH = (1920 / 2 + X_WINDOW) * SCALE
WINDOW_SIZE = 1

MOVE_THRESH = 0.0013

# Minimum centroid position for a crouch position
CROUCH_Y_THRESH = 850 * SCALE

ACTION_KEY = "s"
ACTION_THRESH = 0.002

# Threshold in pixels for one keypress of jumping
JUMP_THRESH = 40 * SCALE
JUMP_KEY = "x"  # z for other game

SECONDS_PER_GAME = 30
