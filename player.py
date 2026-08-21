import pygame

from utils import (
    PLAYER_SPEED,
    ROTATION_FOR_DIRECTION,
    can_move,
    cell_to_pixel_center,
)


class Player:
    """Player class for Pac-Man."""

    def __init__(self, x, y, offset_x, p_p_p=10, gums_coords=None):
        """Initialize the player."""
        self.base_img = pygame.image.load(
            "./assets/player_1.jpg"
        ).convert_alpha()
        self.active_img = pygame.image.load(
            "./assets/activated.jpg"
        ).convert_alpha()
        self.base_img = pygame.transform.scale(self.base_img, (20, 20))
        self.active_img = pygame.transform.scale(self.active_img, (20, 20))
        self.image = self.base_img
        self.direction = "RIGHT"

        self.gums_eated = 0
        self.score = 0
        self.p_p_p = p_p_p
        self.x = x
        self.y = y
        self.offset_x = offset_x
        self.edible = False
        # FIX: mutable default arguments (`gums_coords=set()`) are shared
        # across every instance that doesn't pass one explicitly -- a classic
        # Python pitfall. Default to None and create a fresh set here.
        self.gums_coords = gums_coords if gums_coords is not None else set()
        self.last_time_edible = None

        self.rect = self.image.get_rect(
            center=cell_to_pixel_center(self.x, self.y, self.offset_x)
        )

        self.last_move = 0
        self.moves = {(self.x, self.y)}
        self.speed = PLAYER_SPEED

    def update(self, maze, now):
        if now - self.last_move < self.speed:
            return

        keys = pygame.key.get_pressed()
        moved = False
        new_direction = self.direction

        # Extract direction keys
        UP = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_k]
        DOWN = keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_j]
        LEFT = keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_h]
        RIGHT = keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_l]

        if UP and can_move(maze, self.x, self.y, "UP"):
            self.y -= 1
            new_direction = "UP"
            moved = True

        elif DOWN and can_move(maze, self.x, self.y, "DOWN"):
            self.y += 1
            new_direction = "DOWN"
            moved = True

        elif LEFT and can_move(maze, self.x, self.y, "LEFT"):
            self.x -= 1
            new_direction = "LEFT"
            moved = True

        elif RIGHT and can_move(maze, self.x, self.y, "RIGHT"):
            self.x += 1
            new_direction = "RIGHT"
            moved = True

        if moved:
            self.direction = new_direction
            if (self.edible):
                self.image = pygame.transform.rotate(
                    self.active_img, ROTATION_FOR_DIRECTION[new_direction]
                )
            else:
                self.image = pygame.transform.rotate(
                    self.base_img, ROTATION_FOR_DIRECTION[new_direction]
                )

            pos = (self.x, self.y)
            if pos not in self.moves and pos in self.gums_coords:
                self.score += self.p_p_p
                self.gums_eated += 1

            self.rect = self.image.get_rect(
                center=cell_to_pixel_center(self.x, self.y, self.offset_x)
            )
            self.moves.add(pos)

        self.last_move = now

    def draw(self, screen):
        screen.blit(self.image, self.rect)
