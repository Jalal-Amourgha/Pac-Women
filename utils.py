import json
import sys
import os

from enum import Enum, auto
from pathlib import Path

from custom_print import print_red, print_yellow

# TODO: REPLACE ALL THOSE CONFIG TO BE COMING FROM A CONFIG FILE
CELL_SIZE = 40
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


def can_move(
    maze: list[list[int]], x: int, y: int, direction: str
) -> bool:
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


def cell_to_pixel_center(
    x: int, y: int, offset_x: int, offset_y: int = OFFSET_Y
) -> tuple[int, int]:
    """
    Single source of truth for converting a grid cell to its pixel
    center. offset_x is passed explicitly (rather than read from a global)
    since it depends on the current level's maze width.
    """
    px = offset_x + x * CELL_SIZE + CELL_SIZE // 2
    py = offset_y + y * CELL_SIZE + CELL_SIZE // 2
    return px, py


def read_config() -> dict:
    """Read game config file

    Args:
        path (str): path to config file

    Returns:
        dict: config
    """

    # Detect if the program is bundled (packaged) or not.
    if len(sys.argv) == 1:
        # Try to find config.json automatically in the script's directory
        config_path = Path(writable_path('config.json'))

        if config_path.is_file():
            file_name = config_path
        else:
            print_yellow("Warning: Please provide a config file")
            print_yellow(
                f"Usage: python pac-man.py [config_file] "
                f"(looked for: {config_path})"
            )
            sys.exit(1)

    elif len(sys.argv) == 2:
        file_name = Path(sys.argv[1])

    else:
        print_yellow("Error: Invalid number of arguments")
        print_yellow("Usage: python main.py [config_file]")
        sys.exit(1)

    try:
        with open(file_name, "r") as f:
            config: dict = json.load(f)
    except FileNotFoundError:
        print_red(f"Config file {file_name} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print_red(f"Invalid config file: {file_name}")
        print_red(e)
        sys.exit(1)
    except Exception as e:
        print_red(f"Error reading config file {file_name}")
        print_red(e)
        sys.exit(1)

    return config


def resource_path(relative_path: str) -> str:
    """Get path to resource, works for dev and for PyInstaller bundled exe.

    Resources (assets, fonts) are bundled INSIDE the executable/bundle.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as bundled PyInstaller exe - resources inside bundle
        base_path: str = sys._MEIPASS
    else:
        # Running as script - resources are in script directory
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)


def writable_path(relative_path: str) -> str:
    """Path for writable files (config, highscores).

    In a one-folder bundle: files inside bundle folder (sys._MEIPASS).
    In development: files are next to the script.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as bundled PyInstaller one-folder bundle
        # Config and highscores bundled inside and can be written to
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running as script - use script's directory
        script_dir: str = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(script_dir, relative_path)
