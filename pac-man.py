# TODO: ADD A RESTART BUTTON AFTER THE GAME IS OVER
# TODO: LAUGH AT THE PLAYER IF ITS DIE WITH A SMALL SCORE
# TODO: AFTER PLAYER DIE HE SHOULD BE UNVISIBLE OR UNTOUCHABLE FOR 2 1 OR 2 SEC
import json
import math

import pygame

from button import Button
from custom_print import print_green, print_red
from drawing import Drawing
from ghost import Ghost, cell_to_pixel_center
from mazegenerator.mazegenerator import MazeGenerator
from player import Player
from superGum import SuperGum
from text import TextInput
from utils import (
    CELL_SIZE,
    EDIBLE_BLINK_AT_MS,
    EDIBLE_DURATION_MS,
    State,
    resource_path,
    writable_path,
)
from validation import handle_config_validation


class Game:
    """
    Main game class
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize the game

        Args:
            config (dict): Game configuration
        """

        # Extract window size
        self.SCREEN_WIDTH: int = config["window"]["width"]
        self.SCREEN_HEIGHT: int = config["window"]["height"]

        pygame.init()
        # Create the screen (display serface)
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            # Borderless window
            pygame.NOFRAME | pygame.SCALED,
        )
        pygame.display.set_caption(title="Pac-Man")

        # Clock object to keep tracking of time
        self.clock = pygame.time.Clock()

        self.running = True
        self.highscore_filename = config["player"]["highscore_filename"]
        self.levels: list[dict[str, int]] = config["maps"]
        self.initial_lives = config["player"]["lives"]
        self.p_p_p = config["player"]["points_per_pacgum"]
        self.p_p_s_p = config["player"]["points_per_super_pacgum"]
        self.p_p_g = config["player"]["points_per_ghost"]
        self.level_time = config["player"]["level_max_time"]

        self._fonts: dict = {}

        self.state: State = State.MENU
        self.level_number: int = 0
        self.lives = self.initial_lives
        self.total_score: int = 0
        self.pending_score: int = 0
        self.last_run_won: bool = False
        self.time_left: int = 0

        self.pause_offset: int = 0
        self.paused_since = None

        self.maze: list[list[int]] | None = None
        self.drawing: Drawing | None = None
        self.player: Player | None = None
        self.second_player: Player | None = None
        self.players: list[Player] = []
        self.ghosts: list = []
        self.super_gums: list = []
        self.offset_x: int = 0
        self.rows: int = 0
        self.cols: int = 0
        self.style_42: bool = False
        self.gums_coords: set = set()
        self.total_gums: int = 0

        self.ghost_freeze_until: int = 0

        # C H E A T E - A T T R I B U T E S
        self.invisible = False
        self.stop_time = False

        # Map name => button object
        self.buttons_map: dict[str, Button | TextInput] = {}
        self._build_ui()

        # Sound
        self.very_start_game_sound = pygame.mixer.Sound(
            resource_path("assets/sounds/pac-man-very-start-of-game.wav")
        )
        self.round_start_sound = pygame.mixer.Sound(
            resource_path("assets/sounds/pac-man-start-run.wav")
        )
        self.round_start_delay = 0
        self.player_die_sound = pygame.mixer.Sound(
            resource_path("assets/sounds/pac-man-die.wav")
        )
        self.game_win_sound = pygame.mixer.Sound(
            resource_path("assets/sounds/pac-man-win.wav")
        )
        self.eat_ghost_sound = pygame.mixer.Sound(
            resource_path("assets/sounds/eating-ghost.wav")
        )
        # self.eat_pacgum_sound = pygame.mixer.Sound(
        #     "./assets/sounds/pac-man-eat-pacgum.mp3"
        # )
        # self.eat_super_pacgum_sound = pygame.mixer.Sound(
        #     "./assets/sounds/pac-man-eat-super-pacgum.mp3"
        # )

        self.dual_playing: bool = False
        # Level Info panel stuff
        self.level_panel_font = self._get_font(
            "./fonts/press/PressStart2P.ttf", 16
        )
        live_surf = pygame.image.load(
            resource_path("assets/images/life_heart.png")
        ).convert()
        self.live_surf = pygame.transform.scale(live_surf, (25, 25))

        self.pacwoman_img = pygame.image.load(
            resource_path("assets/images/ms_pacman.png")
        ).convert_alpha()
        self.pacwoman_img = pygame.transform.scale(
            self.pacwoman_img, (539, 874)
        )
        self.pacwoman_img = pygame.transform.flip(
            self.pacwoman_img, True, False
        )
        self.pacwoman_rect = self.pacwoman_img.get_rect(
            bottomleft=(10, self.SCREEN_HEIGHT)
        )

        # animation
        # self.hole_animation = []

    def _get_font(self, path: str, size: int) -> pygame.font.Font:
        """Create the font image if not exists"""
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.Font(resource_path(path), size)
        return self._fonts[key]

    def _centered_x(self, width: int = 220) -> int:
        """Center the button on the x axis of the screen"""
        return (self.SCREEN_WIDTH // 2) - (width // 2)

    def _centered_y(self, height: int = 60) -> int:
        """Center the button on the y axis of the screen"""
        return (self.SCREEN_HEIGHT // 2) - (height // 2)

    def _build_ui(self) -> None:
        """
        Build the UI (mostly buttons)
        """
        big = self._get_font(path="./fonts/pacfont/pac-font.ttf", size=20)

        btn_width, btn_height = 400, 110
        gap: int = 40  # gap between buttons

        menu_items: list[tuple[str, str]] = [
            ("play_btn", "Start Game"),
            ("dual_playing_btn", "Dual Playing"),
            ("instructions_btn", "How To Play"),
            ("leaderbord_btn", "High Scorers"),
            # ("exit_btn", "Exit Game"),
        ]

        # Calculate places based on their total sizes
        total_height: int = (
            len(menu_items) * btn_height + (len(menu_items) - 1) * gap
        )
        start_y: int = (self.SCREEN_HEIGHT // 2) - (total_height // 2)

        # Create Initial buttons
        for i, (button_name, button_text) in enumerate(menu_items):
            y = start_y + i * (btn_height + gap)
            self.buttons_map[button_name] = Button(
                text=button_text,
                x=self._centered_x(btn_width),
                y=y,
                width=btn_width,
                height=btn_height,
                font=big,
            )

        # The rest special buttons
        self.buttons_map["exit_btn"] = Button(
            text="Exit Game",
            x=self._centered_x(btn_width),
            y=self.SCREEN_HEIGHT - 150,
            width=btn_width,
            height=btn_height,
            font=big,
        )

        # self.buttons_map["back_btn"] = Button(
        #     "Back",
        #     self._centered_x(width=btn_width),
        #     self.SCREEN_HEIGHT - 280,
        #     btn_width,
        #     btn_height,
        #     big,
        # )
        self.buttons_map["continue_btn"] = Button(
            "Continue",
            self._centered_x(width=btn_width),
            250,
            btn_width,
            btn_height,
            big,
        )
        self.buttons_map["quit_to_menu_btn"] = Button(
            text="Quit to Menu",
            x=self._centered_x(btn_width),
            y=self.SCREEN_HEIGHT - 280,
            width=btn_width,
            height=btn_height,
            font=big,
        )

        self.buttons_map["submit_btn"] = Button(
            text="Submit",
            x=self._centered_x(width=btn_width),
            y=self._centered_y(height=btn_height),
            width=btn_width,
            height=btn_height,
            font=big,
        )

        self.buttons_map["name_input"] = TextInput(
            x=self._centered_x(width=300),
            y=self._centered_y(height=50) - 20,
            width=300,
            height=50,
            font=self._get_font("./fonts/press/PressStart2P.ttf", 10),
        )
        # TODO: CHECK THIS BUTTON LATER
        self.buttons_map["pause_btn"] = Button(
            "||",
            0,
            0,
            60,
            60,
            big,
        )
        self.buttons_map["resume_btn"] = Button(
            text="Resume",
            x=self._centered_x(btn_width),
            y=self._centered_y(btn_height),
            width=btn_width,
            height=btn_height,
            font=big,
        )

    def now(self) -> int:
        """Return the current game time in milliseconds"""
        return int(pygame.time.get_ticks()) - self.pause_offset

    def _enter_pause(self) -> None:
        """Pause the game and record the pause start time"""
        self.paused_since = pygame.time.get_ticks()
        self.state = State.PAUSED

    def _resume(self) -> None:
        """Resume the game from a paused state"""
        if self.paused_since is not None:
            self.pause_offset += pygame.time.get_ticks() - self.paused_since
            self.paused_since = None
        self.state = State.PLAYING

    def _start_new_run(self) -> None:
        """Reset the run state and start a fresh run"""
        self.level_number = 0
        self.lives = self.initial_lives
        self.total_score = 0
        self.pause_offset = 0
        self.paused_since = None
        self._new_level()
        self.very_start_game_sound.stop()
        self.round_start_sound.play()
        self.round_start_delay = (
            self.now() + self.round_start_sound.get_length() * 1000
        )
        self.state = State.PLAYING

    def _end_run(self, won: bool) -> None:
        """Display the win end game screen"""
        self.pending_score = self.total_score
        self.last_run_won = won
        self.name_input = TextInput(
            self._centered_x(width=300),
            self.SCREEN_HEIGHT // 3,
            300,
            50,
            self._get_font("./fonts/press/PressStart2P.ttf", 18),
        )
        self.state = State.ENTER_NAME

    def _extract_pattern_42(self) -> None:
        """
        Extract the coordinates of the pattern 42
        """
        self.pattern_42_coords = set()
        if not self.style_42:
            return

        coord_42: set = {
            (-3, 0),
            (-2, 0),
            (-1, 0),
            (-3, -1),
            (-3, -2),
            (-1, 1),
            (-1, 2),
            (1, 0),
            (2, 0),
            (3, 0),
            (3, -1),
            (3, -2),
            (2, -2),
            (1, -2),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
        }
        row, col = self.rows, self.cols
        y_even = 1 if not row % 2 else 0
        x_even = 1 if not col % 2 else 0

        if row % 2 == col % 2 and row % 2:
            y_even = 0
            x_even = 0

        for y, x in coord_42:
            self.pattern_42_coords.add(
                (col // 2 + y - x_even, row // 2 + x - y_even)
            )

    def _extract_coords(self) -> None:
        """Extract the corner and gum coordinates for the current level"""
        self.corner_coords = [
            (0, 0),
            (self.cols - 1, 0),
            (0, self.rows - 1),
            (self.cols - 1, self.rows - 1),
        ]
        self._extract_pattern_42()

        # Get all coordinates
        all_coords = {
            (x, y) for x in range(self.cols) for y in range(self.rows)
        }

        self.gums_coords = (
            all_coords - self.pattern_42_coords - set(self.corner_coords)
        )
        self.total_gums = len(self.gums_coords) - 1

    def _new_level(self) -> None:
        """(Re)builds the maze, player, ghosts, and pellets for
        self.level. Used both for starting a fresh run and for advancing
        to the next level within a run."""
        width = self.levels[self.level_number]["width"]
        height = self.levels[self.level_number]["height"]
        self.cols, self.rows = width, height
        self.offset_x = (self.SCREEN_WIDTH - width * CELL_SIZE) // 2
        self.style_42 = width >= 14 and height >= 14

        # Generate the maze with the given width and height
        generator = MazeGenerator(size=(width, height))
        self.maze = generator.maze

        self._extract_coords()
        self.drawing = Drawing(
            self.offset_x, self.corner_coords, self.pattern_42_coords
        )

        # Calculate the closest cell to the center while avoiding 42 pattern
        center_x = self.cols // 2
        center_y = self.rows // 2
        p1_cell: tuple[int, int] = min(
            self.gums_coords,
            key=lambda cell: abs(cell[0] - center_x) + abs(cell[1] - center_y)
        )
        p2_cell: tuple[int, int] = min(
            (cell for cell in self.gums_coords if cell != p1_cell),
            key=lambda cell: abs(cell[0] - center_x) + abs(cell[1] - center_y),
        )
        self.player = Player(
            x=p1_cell[0],
            y=p1_cell[1],
            offset_x=self.offset_x,
            p_p_p=self.p_p_p,
            gums_coords=self.gums_coords,
            dual_playing=self.dual_playing,
        )
        self.second_player = (
            Player(
                x=p2_cell[0],
                y=p2_cell[1],
                offset_x=self.offset_x,
                p_p_p=self.p_p_p,
                gums_coords=self.gums_coords,
                second_player=True,
                dual_playing=True,
            )
            if self.dual_playing
            else None
        )
        self.players = [
            p for p in (self.player, self.second_player) if p is not None
        ]
        self.ghosts = [
            Ghost(gid, x, y, self.offset_x)
            for gid, (x, y) in enumerate(self.corner_coords)
        ]
        self.super_gums = [
            SuperGum(gid, x, y, self.offset_x)
            for gid, (x, y) in enumerate(self.corner_coords)
        ]

        self.level_start_time = self.now()

    def _load_highscores(self) -> list:
        """Load highscores"""
        try:
            with open(writable_path(self.highscore_filename)) as f:
                data = json.load(f)
                if isinstance(data, dict):
                    res = data.get("players", [])
                    if isinstance(res, list):
                        return res
                return []
        except (FileNotFoundError, json.JSONDecodeError):
            # print_red({e})
            return []
        except Exception as e:
            print_red({e})
            return []

    def _save_highscore(self, username: str, score: int) -> None:
        """Saves the highscore"""
        players = self._load_highscores()
        players.append({"username": username or "Player", "score": score})
        with open(writable_path(self.highscore_filename), "w") as f:
            json.dump({"players": players}, f, indent=2)

    def events(self) -> None:
        """Handle events"""

        exit_btn = self.buttons_map["exit_btn"]
        quit_to_menu_btn = self.buttons_map["quit_to_menu_btn"]
        pause_btn = self.buttons_map["pause_btn"]

        for event in pygame.event.get():
            # Check for exit game
            if event.type == pygame.QUIT:
                self.running = False
                return

            # if quit_to_menu_btn.is_clicked(event):
            #     self.state = State.MENU
            #     continue

            # C H E A T E - M O D E
            if event.type == pygame.KEYDOWN:
                # Check if Ctrl is held
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if event.key == pygame.K_1:
                        # P L A Y E R - I N V I S I B L E
                        self.invisible = not self.invisible

                    if event.key == pygame.K_2:
                        # G H O S T - F R E E Z E D
                        for ghost in self.ghosts:
                            ghost.freezed = not ghost.freezed

                    if event.key == pygame.K_3:
                        # P L A Y E R - I N C R E A S E - S P E E D
                        assert self.player is not None
                        self.player.speed = max(self.player.speed - 10, 10)

                    if event.key == pygame.K_4:
                        # P L A Y E R - S K I P - L E V E L
                        assert self.player is not None
                        self.player.gums_eated += self.rows * self.cols
                        self.check_win()

                    if event.key == pygame.K_5:
                        # P L A Y E R - I N C R E A S E - S C O R E by 1000
                        assert self.player is not None
                        self.player.score += 1000

                    if event.key == pygame.K_6:
                        # I M O R T A L E
                        self.lives = math.inf

                    if event.key == pygame.K_7:
                        # S T O P - T I M E
                        self.stop_time = not self.stop_time

            # User inside menu
            if self.state == State.MENU:
                if exit_btn.is_clicked(event):  # type: ignore
                    self.running = False
                    return
                self._handle_menu_event(event)
            elif self.state in (State.INSTRUCTIONS, State.HIGHSCORES):
                if quit_to_menu_btn.is_clicked(event):  # type: ignore
                    self.state = State.MENU
            elif self.state == State.PLAYING:
                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                    or pause_btn.is_clicked(event)  # type: ignore
                ):
                    self._enter_pause()
            elif self.state == State.PAUSED:
                self._handle_pause_event(event)
            elif self.state == State.ENTER_NAME:
                self._handle_enter_name_event(event)

    def _handle_menu_event(self, event: pygame.event.Event) -> None:
        """Handle menu events

        Args:
            event: Pygame event

        """

        # Extract the buttons
        play_btn = self.buttons_map["play_btn"]
        dual_playing_btn = self.buttons_map["dual_playing_btn"]
        instructions_btn = self.buttons_map["instructions_btn"]
        leaderboard_btn = self.buttons_map["leaderbord_btn"]
        exit_btn = self.buttons_map["exit_btn"]

        if play_btn.is_clicked(event):  # type: ignore[union-attr]
            # Set dual_playing back to False
            self.dual_playing = False
            self._start_new_run()
        elif dual_playing_btn.is_clicked(event):  # type: ignore[union-attr]
            self.dual_playing = True
            self._start_new_run()
        elif instructions_btn.is_clicked(event):  # type: ignore[union-attr]
            self.state = State.INSTRUCTIONS
        elif leaderboard_btn.is_clicked(event):  # type: ignore[union-attr]
            self.state = State.HIGHSCORES

        if exit_btn.is_clicked(event):  # type: ignore[union-attr]
            self.running = False

    def _handle_pause_event(self, event: pygame.event.Event) -> None:
        """Handle pause events"""
        pause_btn = self.buttons_map["pause_btn"]
        resume_btn = self.buttons_map["resume_btn"]
        quit_to_menu_btn = self.buttons_map["quit_to_menu_btn"]

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
            or pause_btn.is_clicked(event)  # type: ignore[union-attr]
            or resume_btn.is_clicked(event)  # type: ignore[union-attr]
        ):
            self._resume()
        elif quit_to_menu_btn.is_clicked(event):  # type: ignore[union-attr]
            self.state = State.MENU

    def _handle_enter_name_event(self, event: pygame.event.Event) -> None:
        """Handle the name input while saving the final score

        Args:
            event: Pygame event
        """
        submitted = self.name_input.handle_event(event)
        submit_btn = self.buttons_map["submit_btn"]

        assert isinstance(submit_btn, Button)
        if submitted or submit_btn.is_clicked(event):
            self._save_highscore(
                self.name_input.text.strip(), self.pending_score
            )
            self.state = State.MENU

    def update(self) -> None:
        """Update the game state"""

        if self.state != State.PLAYING:
            return

        # A quick delay at the round start so the player can catchup
        if self.now() < self.round_start_delay:
            return

        now = self.now()
        assert self.players  # silent lints

        for player in self.players:
            assert self.maze is not None
            player.update(self.maze, now)

        # Update ghosts if they not freezed, (freezed immediately after
        # catching the player so he can respawn comfort)
        if self.now() >= self.ghost_freeze_until:
            for ghost in self.ghosts:
                # Check the closest player
                target = min(
                    self.players,
                    key=lambda p: abs(p.x - ghost.x) + abs(p.y - ghost.y),
                )
                ghost.update(
                    maze=self.maze,
                    player_cord=(target.x, target.y),
                    now=now,
                    flee=any(player.edible for player in self.players),
                )
                # Add a delay to the ghost spawn
                if not ghost.alive:
                    elapsed = self.now() - ghost.died_time
                    if elapsed >= 10000:
                        ghost.alive = True

        self._update_edible_state()
        self.check_collisions()

        if self.state == State.PLAYING:
            self.check_win()
        if self.state == State.PLAYING:
            self._update_timer()

    def _update_edible_state(self) -> None:
        """Update the edible timers of all players and ghost forms"""
        any_edible = False
        blink = False
        for player in self.players:
            if not player.edible:
                continue

            elapsed = self.now() - player.last_time_edible  # type: ignore
            if elapsed >= EDIBLE_DURATION_MS:
                player.edible = False
                continue

            any_edible = True
            if elapsed >= EDIBLE_BLINK_AT_MS:
                blink = True

        form: str | None = (
            ("edible_2" if blink else "edible_1") if any_edible else None
        )
        for ghost in self.ghosts:
            if not ghost.alive:
                continue
            ghost.ghost = (
                ghost.forms[form]
                if form is not None
                else ghost.forms[ghost.direction]
            )

    def check_collisions(self) -> None:
        """Check for collisions between the players and ghosts"""
        for ghost in self.ghosts:
            if not ghost.alive:
                continue

            # Check if the ghost collides with a player
            hit_player = next(
                (p for p in self.players if (p.x, p.y) == (ghost.x, ghost.y)),
                None,
            )
            if hit_player is None:
                continue

            if hit_player.edible:
                hit_player.score += self.p_p_g
                ghost.alive = False
                ghost.died_time = self.now()
                ghost.x, ghost.y = self.corner_coords[ghost.id]
                self.eat_ghost_sound.play()
            elif not self.invisible:
                self.player_die_sound.play()
                # IF YOU WANT TO BECOME INVISIBLE PRESS CRTL + 1
                self.lives -= 1
                if self.lives <= 0:
                    # self.game_over_sound.play()

                    self.total_score += sum(p.score for p in self.players)
                    self._end_run(False)
                else:
                    self.ghost_freeze_until = self.now() + 1500
                    hit_player.x, hit_player.y = hit_player.spawn
                    hit_player.rect = hit_player.image.get_rect(
                        center=cell_to_pixel_center(
                            hit_player.x, hit_player.y, self.offset_x
                        )
                    )
            break

        if self.state != State.PLAYING:
            return

        for gum in self.super_gums:
            if gum.eated:
                continue

            eater = next(
                (p for p in self.players if (p.x, p.y) == (gum.x, gum.y)),
                None,
            )
            if eater is None:
                continue

            gum.eated = True
            eater.score += self.p_p_s_p
            eater.edible = True
            eater.last_time_edible = self.now()
            break

    def check_win(self) -> None:
        """Check if the players have cleared the level"""
        eaten_total = sum(p.gums_eated for p in self.players)
        if eaten_total < self.total_gums:
            return

        self.total_score += sum(p.score for p in self.players)
        self.level_number += 1

        if self.level_number == len(self.levels):
            self.game_win_sound.play()
            self._end_run(True)
            # pygame.time.wait(3000)
        else:
            self._new_level()

    def _update_timer(self) -> None:
        """Update the level timer and end the run when time runs out"""
        if self.stop_time:
            return

        self.time_left = self.level_time - (self.now() - self.level_start_time)
        if self.time_left <= 0:
            self.total_score += sum(p.score for p in self.players)
            self._end_run(False)

    def draw(self) -> None:
        """Draw the game based on the current state"""
        if self.state == State.MENU:
            self._draw_menu()
        elif self.state == State.INSTRUCTIONS:
            self._draw_instructions()
        elif self.state == State.HIGHSCORES:
            self._draw_highscores()
        elif self.state in (State.PLAYING, State.PAUSED):
            self._draw_game()
            if self.state == State.PAUSED:
                self._draw_pause_overlay()
        elif self.state == State.ENTER_NAME:
            self._draw_enter_name()

        pygame.display.flip()

    def _draw_title(
        self,
        text: str = "Pac Women",
        color: str = "yellow",
        creator: bool = False,
    ) -> None:
        """Draws the game title"""

        # text_font = self._get_font("./fonts/pacfont/pac-font.ttf", 30)
        text_font = self._get_font("./fonts/arcade/ARCADE_I.TTF", 60)
        game_name = text_font.render(text, False, color)
        game_name_rect = game_name.get_rect(
            center=(self.SCREEN_WIDTH // 2, 70)
        )
        self.screen.blit(game_name, game_name_rect)

        if creator:
            creator_font = self._get_font("./fonts/press/PressStart2P.ttf", 10)
            creator_font.set_italic(True)
            creator_name = creator_font.render(
                "By jamourgh & aarid", False, color
            )
            creator_rect = creator_name.get_rect(
                center=(self.SCREEN_WIDTH // 2, 110)
            )
            self.screen.blit(creator_name, creator_rect)

    def _draw_menu(self) -> None:
        """Draws the main menu"""
        self.screen.fill((0, 0, 0))  # Clear screen with black background
        self._draw_title(creator=True)
        menu_buttons = [
            self.buttons_map["play_btn"],
            self.buttons_map["dual_playing_btn"],
            self.buttons_map["instructions_btn"],
            self.buttons_map["leaderbord_btn"],
            self.buttons_map["exit_btn"],
        ]

        for btn in menu_buttons:
            btn.draw(self.screen)

        # Draw the ms pacwoman
        self.screen.blit(self.pacwoman_img, self.pacwoman_rect)

    def _draw_instructions(self) -> None:
        """Draws the instructions screen"""
        self.screen.fill((0, 0, 0))
        self._draw_title("How To Play")

        lines = [
            "Move with the Arrow Keys or WASD.",
            "Walk over pellets to score points.",
            "Avoid the ghosts - they will chase you!",
            "Grab a super gum: ghosts turn edible and flee.",
            "Eat a fleeing ghost for bonus points.",
            "Clear every pellet to finish the level.",
            "Press ESC to pause at any time.",
        ]
        text_font = self._get_font("./fonts/press/PressStart2P.ttf", 18)
        for i, line in enumerate(lines):
            surf = text_font.render(line, False, "white")
            rect = surf.get_rect(center=(self.SCREEN_WIDTH // 2, 300 + i * 40))
            self.screen.blit(surf, rect)

        quit_to_menu_btn = self.buttons_map["quit_to_menu_btn"]
        quit_to_menu_btn.draw(self.screen)

    def _draw_highscores(self) -> None:
        """Draws the highscores screen"""
        self.screen.fill((0, 0, 0))
        self._draw_title("Top Players")

        quit_to_menu_btn = self.buttons_map["quit_to_menu_btn"]
        quit_to_menu_btn.draw(self.screen)

        players: list = sorted(
            self._load_highscores(), key=lambda p: -p["score"]
        )
        text_font = self._get_font("./fonts/press/PressStart2P.ttf", 18)
        record_height: int = 60
        record_width: int = 240

        if not players:
            surf = text_font.render(
                "No scores yet - be the first!", False, "white"
            )
            rect = surf.get_rect(
                center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 4)
            )
            self.screen.blit(surf, rect)
        else:
            for idx, player in enumerate(players[:10]):
                color = "white"
                if idx == 0:
                    color = "#FFD700"
                elif idx == 1:
                    color = "#C0C0C0"
                elif idx == 2:
                    color = "#CD7F32"
                # else:
                #     name_surf = text_font.render(
                #         str(player['username']), False, 'white')

                # name_surf = text_font.render(
                #     f"{idx + 1}- {player['username']}", False, color
                # )
                # score_surf = text_font.render(
                #     str(player["score"]), False, color
                # )
                #
                player_record_surf = text_font.render(
                    f"{idx + 1}- {player['username']}: {player['score']}",
                    False,
                    color,
                )
                self.screen.blit(
                    player_record_surf,
                    player_record_surf.get_rect(
                        topleft=(
                            self._centered_x(width=record_width) - 40,
                            self.SCREEN_HEIGHT // 6 + (record_height * idx),
                        )
                    ),
                )
                # self.screen.blit(
                #     score_surf,
                #     score_surf.get_rect(topleft=(500, 130 + idx * 30)),
                # )

    def _draw_enter_name(self) -> None:
        """Draws the enter name screen after a game is over"""

        # Extract buttons
        submit_btn = self.buttons_map["submit_btn"]
        quit_to_menu_btn = self.buttons_map["quit_to_menu_btn"]

        # For score and prompt
        text_font = self._get_font("./fonts/press/PressStart2P.ttf", 16)

        self.screen.fill((0, 0, 0))
        if self.last_run_won:
            self._draw_title("You Win!", "green")
        else:
            self._draw_title("Game Over", "red")

        score_surf = text_font.render(
            f"Final score: {self.pending_score}", False, "white"
        )
        self.screen.blit(
            score_surf,
            score_surf.get_rect(
                center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 6)
            ),
        )

        prompt_surf = text_font.render("Enter your name:", False, "white")
        self.screen.blit(
            prompt_surf,
            prompt_surf.get_rect(
                center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 4)
            ),
        )

        self.name_input.draw(self.screen)
        submit_btn.draw(self.screen)
        quit_to_menu_btn.draw(self.screen)

    def _draw_game(self) -> None:
        """Draws the game screen"""
        self.screen.fill((0, 0, 0))
        self._draw_title(creator=True)
        self._draw_level_info()
        self.buttons_map["pause_btn"].draw(self.screen)

        # Pellets disappear once any player has stepped on them
        eaten_cells: set = set()
        for player in self.players:
            eaten_cells |= player.moves

        assert self.maze is not None
        assert self.drawing is not None
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                self.drawing.draw_cell(self.screen, cell, x, y, eaten_cells)

        for ghost in self.ghosts:
            ghost.draw(self.screen)
        for gum in self.super_gums:
            gum.draw(self.screen)

        # Collect all the pygame characters objects
        sprites = pygame.sprite.Group(self.players)

        # Draw all the characters(sprites)
        sprites.draw(self.screen)

        # self.player.draw(self.screen)

    def _draw_level_info(self) -> None:
        """Draws the level info panel"""

        if self.dual_playing:
            score_text = (
                f"P1: {self.players[0].score}   P2: {self.players[1].score}"
            )
        else:
            score_text = f"Score: {self.players[0].score}"

        score_surf = self.level_panel_font.render(score_text, False, "white")
        timer_surf = self.level_panel_font.render(
            f"Timer: {max(self.time_left, 0) // 1000}", False, "white"
        )
        cur_level = self.level_number + 1
        total_levels = len(self.levels)
        level_surf = self.level_panel_font.render(
            f"Level: {cur_level}/{total_levels}", False, "white"
        )

        # pygame.draw.line(
        #     self.screen, "white", (0, 170), (self.SCREEN_WIDTH, 170), 3
        # )
        self.screen.blit(score_surf, score_surf.get_rect(topleft=(100, 130)))

        # Draw lives hearts
        gap: int = 0
        for _ in range(self.lives):
            self.screen.blit(
                source=self.live_surf,
                dest=self.live_surf.get_rect(topleft=(100 + gap, 80)),
            )
            gap += 40

        self.screen.blit(
            timer_surf,
            timer_surf.get_rect(topright=(self.SCREEN_WIDTH - 100, 130)),
        )
        self.screen.blit(
            level_surf,
            level_surf.get_rect(topright=(self.SCREEN_WIDTH - 300, 130)),
        )

    def _draw_pause_overlay(self) -> None:
        """Draws the pause overlay"""

        quit_to_menu_btn = self.buttons_map["quit_to_menu_btn"]
        resume_btn = self.buttons_map["resume_btn"]

        overlay = pygame.Surface(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        text_font = self._get_font("./fonts/pacfont/pac-font.ttf", 40)
        text = text_font.render("Paused", False, "yellow")
        self.screen.blit(
            text, text.get_rect(center=(self.SCREEN_WIDTH // 2, 150))
        )

        resume_btn.draw(self.screen)
        # self.paus_btn.draw(self.screen)
        quit_to_menu_btn.draw(self.screen)

    def run(self) -> None:
        """Runs the game"""
        self.very_start_game_sound.play()
        while self.running:
            self.events()
            self.update()
            self.draw()
            # Limit to 60 frames per second
            self.clock.tick(60)

        pygame.quit()


def main() -> None:
    """Main function"""

    config: dict = handle_config_validation()
    pacman = Game(config)
    pacman.run()
    print_green("Thanks for playing!")


if __name__ == "__main__":
    main()
