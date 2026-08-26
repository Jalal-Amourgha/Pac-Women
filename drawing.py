import pygame

from utils import CELL_SIZE, OFFSET_Y, WALL_SIZE


class Drawing:
    """Draws the maze on the screen"""

    def __init__(
        self,
        offset_x: int,
        super_gums_coords: set[tuple[int, int]],
        pattern_42_coords: set[tuple[int, int]],
    ) -> None:
        """Initializes the drawing object"""
        self.offset_x = offset_x
        self.super_gums_coords = super_gums_coords
        self.pattern_42_coords = pattern_42_coords

    def draw_cell(
        self,
        screen: pygame.Surface,
        cell: int,
        x: int,
        y: int,
        player_moves: set,
    ) -> None:
        """Draws a cell on the screen based on its value and position

        Args:
            screen (pygame.Surface): The surface to draw on
            cell (int): The value of the cell
            x (int): The x position of the cell
            y (int): The y position of the cell
            player_moves (set): The set of moves made by the player

        Returns:
            None
        """
        px = self.offset_x + x * CELL_SIZE
        py = OFFSET_Y + y * CELL_SIZE

        if (x, y) in self.pattern_42_coords:
            pygame.draw.rect(screen, "yellow", (px, py, CELL_SIZE, CELL_SIZE))
        elif (x, y) not in player_moves and (
            x,
            y,
        ) not in self.super_gums_coords:
            pygame.draw.circle(screen, "yellow", (px + 15, py + 15), 5)

        if cell & 1:
            pygame.draw.line(
                screen, "blue", (px, py), (px + CELL_SIZE, py), WALL_SIZE
            )
        if cell & 2:
            pygame.draw.line(
                screen,
                "blue",
                (px + CELL_SIZE, py),
                (px + CELL_SIZE, py + CELL_SIZE),
                WALL_SIZE,
            )
        if cell & 4:
            pygame.draw.line(
                screen,
                "blue",
                (px, py + CELL_SIZE),
                (px + CELL_SIZE, py + CELL_SIZE),
                WALL_SIZE,
            )
        if cell & 8:
            pygame.draw.line(
                screen, "blue", (px, py), (px, py + CELL_SIZE), WALL_SIZE
            )
