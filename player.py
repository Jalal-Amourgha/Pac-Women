import pygame
from utils import *

class Player:
    def __init__(self, x, y, offset_x, p_p_p=10, gums_coords=None):
        self.base_image = pygame.image.load('./assets/player_1.jpg').convert_alpha()
        self.base_image = pygame.transform.scale(self.base_image, (20, 20))
        self.image = self.base_image
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

        self.rect = self.image.get_rect(center=cell_to_pixel_center(self.x, self.y, self.offset_x))

        self.last_move = 0
        self.moves = {(self.x, self.y)}

    def update(self, maze, now):
        if now - self.last_move < PLAYER_SPEED:
            return

        keys = pygame.key.get_pressed()
        moved = False
        new_direction = self.direction

        if (keys[pygame.K_UP] or keys[pygame.K_w]) and can_move(maze, self.x, self.y, "UP"):
            self.y -= 1
            new_direction = "UP"
            moved = True
        elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and can_move(maze, self.x, self.y, "DOWN"):
            self.y += 1
            new_direction = "DOWN"
            moved = True
        elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and can_move(maze, self.x, self.y, "LEFT"):
            self.x -= 1
            new_direction = "LEFT"
            moved = True
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and can_move(maze, self.x, self.y, "RIGHT"):
            self.x += 1
            new_direction = "RIGHT"
            moved = True

        if moved:
            self.direction = new_direction
            self.image = pygame.transform.rotate(self.base_image, ROTATION_FOR_DIRECTION[new_direction])

            pos = (self.x, self.y)
            if pos not in self.moves and pos in self.gums_coords:
                self.score += self.p_p_p
                self.gums_eated += 1

            self.rect = self.image.get_rect(center=cell_to_pixel_center(self.x, self.y, self.offset_x))
            self.moves.add(pos)

        self.last_move = now

    def draw(self, screen):
        screen.blit(self.image, self.rect)