import pygame

from utils import (
    PLAYER_SPEED,
    ROTATION_FOR_DIRECTION,
    can_move,
    cell_to_pixel_center,
    resource_path,
)


class Player(pygame.sprite.Sprite):
    """Player class for Pac-Man."""

    def __init__(
        self,
        x: int,
        y: int,
        offset_x: int,
        p_p_p: int = 10,
        gums_coords: set[tuple[int, int]] | None = None,
        second_player: bool = False,
        dual_playing: bool = False,
    ) -> None:
        """Initialize the player."""
        super().__init__()

        # Load player frames
        base_img = pygame.image.load(
            resource_path("assets/images/player_frame1.jpg")
        ).convert_alpha()
        action_img = pygame.image.load(
            resource_path("assets/images/player_frame2.jpg")
        )

        active_img = pygame.image.load(
            resource_path("assets/images/activated.jpg")
        ).convert_alpha()

        self.base_img = pygame.transform.scale(base_img, (25, 25))
        self.action_img = pygame.transform.scale(action_img, (25, 25))
        self.active_img = pygame.transform.scale(active_img, (25, 25))
        self.image = self.base_img

        # Set animation frames
        self.frames: list = [
            self.base_img,  # mouth closed
            self.action_img,  # mouth open
        ]
        self.frame_index: int = 0
        self.frame_timer: int = 0

        self.direction = "RIGHT"
        self.gums_eated = 0
        self.score = 0
        self.p_p_p = p_p_p
        self.x = x
        self.y = y
        self.spawn = (x, y)
        self.offset_x = offset_x
        self.edible = False
        # FIX: mutable default arguments (`gums_coords=set()`) are shared
        # across every instance that doesn't pass one explicitly -- a classic
        # Python pitfall. Default to None and create a fresh set here.
        self.gums_coords = gums_coords if gums_coords is not None else set()
        self.last_time_edible: int | None = None

        self.rect = self.image.get_rect(
            center=cell_to_pixel_center(self.x, self.y, self.offset_x)
        )

        self.last_move = 0
        self.moves = {(self.x, self.y)}
        self.speed: int = PLAYER_SPEED
        # Feature for dual playing
        self.second_player: bool = second_player
        self.dual_playing: bool = dual_playing

        # Sounds
        self.eat_dot_sound = pygame.mixer.Sound(
            resource_path("assets/sounds/pacman-eat-dots.wav")
        )

    def update(self, maze: list[list[int]], now: int) -> None:
        """Update the player's position based on the maze and the current time.

        Args:
            maze (list): The maze layout.
            now (int): The current time in milliseconds.
        """
        if now - self.last_move < self.speed:
            return

        moved = False
        new_direction = self.direction

        # Get the playing keys based on the used mode (single or dual)
        UP, DOWN, LEFT, RIGHT = self._handle_playing_mode()

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

        # Animate the player (switch the frame every 100ms)
        if now - self.frame_timer >= 200:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.frame_timer = now

            src_img = self.frames[self.frame_index]

            self.image = pygame.transform.rotate(
                src_img,
                ROTATION_FOR_DIRECTION[self.direction],
            )
        else:
            # Initialize src_img with the current frame
            src_img = self.frames[self.frame_index]

        # Check if the player has eaten a gum
        pos = (self.x, self.y)
        if pos not in self.moves and pos in self.gums_coords:
            self.eat_dot_sound.play()
            self.score += self.p_p_p
            self.gums_eated += 1

        # Rotate if the player has moved and register the move.
        if moved:
            self.direction = new_direction

            # TODO: UPDATE LATER TO STORE THE ROTATED AND JUST
            # INSTEAD OF CALCULATING IT EACH TIME.
            self.image = pygame.transform.rotate(
                src_img, ROTATION_FOR_DIRECTION[new_direction]
            )

            # NOTE: WHY THIS?
            self.rect = self.image.get_rect(
                center=cell_to_pixel_center(self.x, self.y, self.offset_x)
            )
            self.moves.add(pos)

        self.last_move = now

    def _handle_playing_mode(self) -> tuple[bool, bool, bool, bool]:
        """Handle the playing keys based on the used mode

        Single player:
            Can play with WASD, KJHL, or arrow keys

        Dual player:
            1p: Can play with WASD
            2p: Can play with KJHL, or arrow keys

        Returns:
            tuple(bool, bool, bool, bool): The playing keys
        """

        keys = pygame.key.get_pressed()
        UP, DOWN, LEFT, RIGHT = False, False, False, False

        # Extract direction keys, if one player, it can play with several keys
        if not self.dual_playing:
            UP = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_k]
            DOWN = keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_j]
            LEFT = keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_h]
            RIGHT = (
                keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_l]
            )
        if self.dual_playing and self.second_player:
            UP = keys[pygame.K_UP] or keys[pygame.K_k]
            DOWN = keys[pygame.K_DOWN] or keys[pygame.K_j]
            LEFT = keys[pygame.K_LEFT] or keys[pygame.K_h]
            RIGHT = keys[pygame.K_RIGHT] or keys[pygame.K_l]

        if self.dual_playing and not self.second_player:
            UP = keys[pygame.K_w]
            DOWN = keys[pygame.K_s]
            LEFT = keys[pygame.K_a]
            RIGHT = keys[pygame.K_d]

        return UP, DOWN, LEFT, RIGHT
