import random
from collections import deque

import pygame

# TODO: REPLACE ALL THOSE CONFIG TO BE COMING FROM A CONFIG FILE, later.
from utils import (
    DIRECTIONS,
    GHOST_CHASE_CHANCE,
    GHOST_SPEED,
    can_move,
    cell_to_pixel_center,
)


class Ghost:
    """Ghost class for Pac-Man."""

    def __init__(self, id: int, x: int, y: int, offset_x: int) -> None:
        """Initialize the ghost."""
        self.id: int = id
        self.alive: bool = True
        self.forms = self._setup_ghosts()
        self.direction: str = "DOWN"
        self.ghost = self.forms[self.direction]
        self.x: int = x
        self.y: int = y
        self.offset_x: int = offset_x
        self.last_move: int = 0
        self.rect = self.ghost.get_rect(
            center=cell_to_pixel_center(self.x, self.y, self.offset_x)
        )
        self.died_time = None
        self.freezed = False

    def _setup_ghosts(self) -> dict[str, pygame.Surface]:
        """Setup the ghosts forms"""
        forms: dict = {}
        for form in ("UP", "RIGHT", "DOWN", "LEFT"):
            img_path: str = (
                f"./assets/images/ghost_{self.id + 1}_{form.lower()}.jpg"
            )

            ghost_form_img = pygame.image.load(img_path).convert_alpha()
            forms[form] = pygame.transform.scale(ghost_form_img, (25, 25))

        forms["edible_1"] = pygame.transform.scale(
            pygame.image.load("./assets/images/edible_1.jpg").convert_alpha(),
            (25, 25),
        )
        forms["edible_2"] = pygame.transform.scale(
            pygame.image.load("./assets/images/edible_2.jpg").convert_alpha(),
            (25, 25),
        )

        return forms

    def bfs(
        self, maze: list[list[int]], goal: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Breadth-first search algorithm

        Args:
            maze (list[list[int]]): The maze layout
            goal (tuple[int, int]): Target cell coordinates

        Returns:
            list[tuple[int, int]]: Path from the ghost cell to the goal,
            empty if unreachable
        """
        rows = len(maze)
        cols = len(maze[0])
        start = (self.x, self.y)

        if start == goal:
            return []

        visited = {start}
        queue: deque[
            tuple[tuple[int, int], list[tuple[int, int]]]
        ] = deque([(start, [])])

        while queue:
            (x, y), path = queue.popleft()

            for direction, dx, dy in DIRECTIONS:
                if not can_move(maze, x, y, direction):
                    continue

                nx, ny = x + dx, y + dy
                if (
                    not (0 <= nx < cols and 0 <= ny < rows)
                    or (nx, ny) in visited
                ):
                    continue

                new_path = path + [(nx, ny)]
                if (nx, ny) == goal:
                    return new_path

                visited.add((nx, ny))
                queue.append(((nx, ny), new_path))

        return []

    def _step_to(self, nx: int, ny: int) -> bool:
        """Move the ghost one cell to (nx, ny) and update its form"""
        dx, dy = nx - self.x, ny - self.y
        for direction, ddx, ddy in DIRECTIONS:
            if (ddx, ddy) == (dx, dy):
                self.x, self.y = nx, ny
                self.direction = direction
                self.ghost = self.forms[direction]
                return True
        return False

    def _move_toward(
        self, maze: list[list[int]], goal: tuple[int, int]
    ) -> bool:
        """Move the ghost one step along the shortest path to the goal"""
        path = self.bfs(maze, goal)
        if not path:
            return False
        nx, ny = path[0]
        return self._step_to(nx, ny)

    def _move_away(
        self, maze: list[list[int]], player_cord: tuple[int, int]
    ) -> bool:
        """Move the ghost to the neighboring cell farthest from the player"""
        best = None
        best_dist = -1
        options = DIRECTIONS[:]
        random.shuffle(options)

        for direction, dx, dy in options:
            if not can_move(maze, self.x, self.y, direction):
                continue
            nx, ny = self.x + dx, self.y + dy
            dist = abs(nx - player_cord[0]) + abs(ny - player_cord[1])
            if dist > best_dist:
                best_dist = dist
                best = (nx, ny)

        if best is None:
            return False
        return self._step_to(*best)

    def _move_random(self, maze: list[list[int]]) -> bool:
        """Move the ghost to a random available neighboring cell"""
        dirs = DIRECTIONS[:]
        random.shuffle(dirs)
        for direction, dx, dy in dirs:
            if can_move(maze, self.x, self.y, direction):
                self.x += dx
                self.y += dy
                self.direction = direction
                self.ghost = self.forms[direction]
                return True
        return False

    def update(
        self,
        maze: list[list[int]],
        player_cord: tuple[int, int],
        now: int,
        flee: bool = False,
    ) -> None:
        """
        Update the ghost position based on the maze and the current time

        Args:
            maze (list[list[int]]): The maze layout
            player_cord (tuple[int, int]): The closest player cell
            now (int): The current time in milliseconds
            flee (bool): True when the ghost must run away from the player
        """
        if not self.alive or self.freezed:
            return

        if now - self.last_move < GHOST_SPEED:
            return

        if flee:
            moved = self._move_away(maze, player_cord)
        else:
            moved = random.random() < GHOST_CHASE_CHANCE and self._move_toward(
                maze, player_cord
            )

        if not moved:
            moved = self._move_random(maze)

        if moved:
            self.rect = self.ghost.get_rect(
                center=cell_to_pixel_center(self.x, self.y, self.offset_x)
            )

        self.last_move = now

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the ghost on the screen if alive

        Args:
            screen: Pygame screen
        """
        if self.alive:
            screen.blit(self.ghost, self.rect)
