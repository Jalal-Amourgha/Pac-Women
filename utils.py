from enum import Enum, auto
from sys import exit

import toml

from custom_print import print_red

# TODO: REPLACE ALL THOSE CONFIG TO BE COMING FROM A CONFIG FILE
CELL_SIZE = 30
WALL_SIZE = 4

OFFSET_Y = 170

PLAYER_SPEED = 100
GHOST_SPEED = 300

GHOST_CHASE_CHANCE = 0.8

EDIBLE_DURATION_MS = 10000
EDIBLE_BLINK_AT_MS = 5000

DIRECTIONS: list[tuple[str, int, int]] = [
    ("UP", 0, -1),
    ("RIGHT", 1, 0),
    ("DOWN", 0, 1),
    ("LEFT", -1, 0),
]

ROTATION_FOR_DIRECTION: dict[str, int] = {
    "UP": 90,
    "RIGHT": 0,
    "DOWN": 270,
    "LEFT": 180,
}


class State(Enum):
    MENU = auto()
    INSTRUCTIONS = auto()
    HIGHSCORES = auto()
    PLAYING = auto()
    PAUSED = auto()
    ENTER_NAME = auto()


def can_move(maze, x, y, direction: str):
    """
    Returns true if the player can move in the given direction
    """

    cell = maze[y][x]

    if direction == "UP":
        return cell & 1 == 0

    if direction == "RIGHT":
        return cell & 2 == 0

    if direction == "DOWN":
        return cell & 4 == 0

    if direction == "LEFT":
        return cell & 8 == 0

    return False


def cell_to_pixel_center(x, y, offset_x, offset_y=OFFSET_Y):
    """
    Single source of truth for converting a grid cell to its pixel
    center. offset_x is passed explicitly (rather than read from a global)
    since it depends on the current level's maze width.
    """
    px = offset_x + x * CELL_SIZE + CELL_SIZE // 2
    py = offset_y + y * CELL_SIZE + CELL_SIZE // 2
    return px, py


def read_config(path: str) -> dict:
    """Read game config file

    Args:
        path (str): path to config file

    Returns:
        dict: config
    """

    try:
        with open(path) as f:
            config = toml.load(f)
    except FileNotFoundError:
        print_red("Error: Config file not found")
        exit(1)
    except toml.TomlDecodeError as e:
        print_red("Error: Invalid config file ")
        print_red(e)
        exit(1)
    except Exception as e:
        print_red(f"{type(e).__name__}: {e}")
        exit(1)

    return config
