import random
import pygame
from collections import deque
from mazegenerator.mazegenerator import MazeGenerator
import json


CELL_SIZE = 30
WALL_SIZE = 4

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

OFFSET_Y = 170

PLAYER_SPEED = 100
GHOST_SPEED = 300

GHOST_CHASE_CHANCE = 0.8

EDIBLE_DURATION_MS = 10000
EDIBLE_BLINK_AT_MS = 5000

DIRECTIONS = [
    ("UP", 0, -1),
    ("RIGHT", 1, 0),
    ("DOWN", 0, 1),
    ("LEFT", -1, 0),
]

ROTATION_FOR_DIRECTION = {
    "UP": 90,
    "RIGHT": 0,
    "DOWN": 270,
    "LEFT": 180,
}


class State:
    MENU = "menu"
    INSTRUCTIONS = "instructions"
    HIGHSCORES = "highscores"
    PLAYING = "playing"
    PAUSED = "paused"
    ENTER_NAME = "enter_name"



def can_move(maze, x, y, direction):
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
