import json

import pygame
import random

from button import *
from drawing import *
from ghost import *
from mazegenerator.mazegenerator import MazeGenerator
from parser import *
from player import *
from superGum import *
from text import *
from utils import *

# NOTE: DO NOT IMPORT BLINDLY WITH '*', USE SPECIFIC MODULES


class Game:
    """
    Main game class
    """

    def __init__(self, config):
        """
        Initialize the game
        """

        pygame.init()
        # Create the screen
        self.screen = pygame.display.set_mode(
            size=(SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption(title="Pac-Man")

        # Clock object to keep tracking of time
        self.clock = pygame.time.Clock()

        self.running = True
        self.highscore_filename = config["highscore_filename"]
        self.levels = config["level"]
        self.initial_lives = config["lives"]
        self.p_p_p = config["points_per_pacgum"]
        self.p_p_s_p = config["points_per_super_pacgum"]
        self.p_p_g = config["points_per_ghost"]
        self.level_time = config.get("level_max_time", 900000)

        self._fonts: dict = {}

        self.state = State.MENU
        self.level: int = 0
        self.lives = self.initial_lives
        self.total_score: int = 0
        self.pending_score: int = 0
        self.last_run_won: bool = False
        self.time_left: int = 0

        self.pause_offset: int = 0
        self.paused_since = None

        self.maze = None
        self.drawing = None
        self.player = None
        self.ghosts: list = []
        self.super_gums: list = []
        self.offset_x: int = 0
        self.rows: int = 0
        self.cols: int = 0
        self.style_42: bool = False
        self.gums_coords: set = set()
        self.total_gums: int = 0

        self._build_ui()

    def _font(self, path, size):
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.Font(path, size)
        return self._fonts[key]

    def _build_ui(self):
        """
        Build the UI (mostly buttons)
        """
        big = self._font("./fonts/pacfont/pac-font.ttf", 20)

        self.play_btn = Button("Start Game", 300, 200, 220, 60, big)
        self.instructions_btn = Button("How To Play", 300, 280, 220, 60, big)
        self.leader_btn = Button("High Scorers", 300, 360, 220, 60, big)
        self.exit_btn = Button("Exit Game", 300, 440, 220, 60, big)

        self.back_btn = Button("Back", 300, 500, 220, 60, big)

        self.paus_btn = Button("Continue", 300, 250, 220, 60, big)
        self.quit_to_menu_btn = Button("Quit to Menu", 300, 330, 220, 60, big)

        self.submit_btn = Button("Submit", 300, 330, 220, 60, big)
        self.name_input = TextInput(
            250, 250, 300, 50, self._font("./fonts/press/PressStart2P.ttf", 10)
        )

    def now(self):
        return pygame.time.get_ticks() - self.pause_offset

    def _enter_pause(self):
        self.paused_since = pygame.time.get_ticks()
        self.state = State.PAUSED

    def _resume(self):
        if self.paused_since is not None:
            self.pause_offset += pygame.time.get_ticks() - self.paused_since
            self.paused_since = None
        self.state = State.PLAYING

    def _start_new_run(self):
        self.level: int = 0
        self.lives: int = self.initial_lives
        self.total_score: int = 0
        self.pause_offset: int = 0
        self.paused_since: int | None = None
        self._new_level()
        self.state = State.PLAYING

    def _end_run(self, won):
        self.pending_score = self.total_score
        self.last_run_won = won
        self.name_input = TextInput(
            250, 250, 300, 50, self._font("./fonts/press/PressStart2P.ttf", 18)
        )
        self.state = State.ENTER_NAME

    def _extract_pattern_42(self):
        """
        Extract the coordinates of the pattern 42
        """
        self.pattern_42_coords = set()
        if not self.style_42:
            return

        coord_42 = {
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

    def _extract_coords(self):
        """ """
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

    def _new_level(self):
        """(Re)builds the maze, player, ghosts, and pellets for
        self.level. Used both for starting a fresh run and for advancing
        to the next level within a run."""
        width = self.levels[self.level]["width"]
        height = self.levels[self.level]["height"]
        self.cols, self.rows = width, height
        self.offset_x = (SCREEN_WIDTH - width * CELL_SIZE) // 2
        self.style_42 = width >= 14 and height >= 14

        generator = MazeGenerator(size=(width, height))
        self.maze = generator.maze

        self._extract_coords()
        self.drawing = Drawing(
            self.offset_x, self.corner_coords, self.pattern_42_coords
        )

        self.player = Player(3, 3, self.offset_x, self.p_p_p, self.gums_coords)
        self.ghosts = [
            Ghost(gid, x, y, self.offset_x)
            for gid, (x, y) in enumerate(self.corner_coords)
        ]
        self.super_gums = [
            SuperGum(gid, x, y, self.offset_x)
            for gid, (x, y) in enumerate(self.corner_coords)
        ]

        self.level_start_time = self.now()

    def _load_highscores(self):
        try:
            with open(self.highscore_filename) as f:
                return json.load(f).get("players", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_highscore(self, username, score):
        players = self._load_highscores()
        players.append({"username": username or "Player", "score": score})
        with open(self.highscore_filename, "w") as f:
            json.dump({"players": players}, f, indent=2)

    def events(self):
        """Handle events"""
        for event in pygame.event.get():
            # Check for exit game
            if event.type == pygame.QUIT or self.exit_btn.is_clicked(event):
                self.running = False
                continue
            # User inside menu
            if self.state == State.MENU:
                self._handle_menu_event(event)
            elif self.state in (State.INSTRUCTIONS, State.HIGHSCORES):
                if self.back_btn.is_clicked(event):
                    self.state = State.MENU
            elif self.state == State.PLAYING:
                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    self._enter_pause()
            elif self.state == State.PAUSED:
                self._handle_pause_event(event)
            elif self.state == State.ENTER_NAME:
                self._handle_enter_name_event(event)

    def _handle_menu_event(self, event):
        if self.play_btn.is_clicked(event):
            self._start_new_run()
        elif self.instructions_btn.is_clicked(event):
            self.state = State.INSTRUCTIONS
        elif self.leader_btn.is_clicked(event):
            self.state = State.HIGHSCORES

        if self.exit_btn.is_clicked(event):
            self.running = False

    def _handle_pause_event(self, event):
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
            or self.paus_btn.is_clicked(event)
        ):
            self._resume()
        elif self.quit_to_menu_btn.is_clicked(event):
            self.state = State.MENU

    def _handle_enter_name_event(self, event):
        submitted = self.name_input.handle_event(event)
        if submitted or self.submit_btn.is_clicked(event):
            self._save_highscore(
                self.name_input.text.strip(), self.pending_score
            )
            self.state = State.MENU

    def update(self):
        """Update the game state"""

        if self.state != State.PLAYING:
            return

        now = self.now()
        assert self.player is not None  # silent lints
        self.player.update(self.maze, now)
        for ghost in self.ghosts:
            ghost.update(
                maze=self.maze,
                player_cord=(self.player.x, self.player.y),
                now=now,
                flee=self.player.edible,
            )
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

    def _update_edible_state(self):
        """"""
        if not self.player.edible:
            return

        elapsed = self.now() - self.player.last_time_edible
        if elapsed >= EDIBLE_DURATION_MS:
            self.player.edible = False
            for ghost in self.ghosts:
                if ghost.alive:
                    ghost.ghost = ghost.forms[ghost.direction]
            return

        blink_form: str = (
            "edible_2" if elapsed >= EDIBLE_BLINK_AT_MS else "edible_1"
        )
        for ghost in self.ghosts:
            if ghost.alive:
                ghost.ghost = ghost.forms[blink_form]

    def check_collisions(self):
        assert self.player is not None
        for ghost in self.ghosts:
            if not ghost.alive or (ghost.x, ghost.y) != (
                self.player.x,
                self.player.y,
            ):
                continue

            if self.player.edible:
                self.player.score += self.p_p_g
                ghost.alive = False
                ghost.died_time = self.now()
                ghost.x = self.corner_coords[ghost.id][0]
                ghost.y = self.corner_coords[ghost.id][1]
            else:
                self.lives -= 1
                # if self.lives <= 0:
                #     self.total_score += self.player.score
                #     self._end_run(False)
                # else:
                #     self.player.x, self.player.y = (3, 3)
                #     self.player.rect = self.player.image.get_rect(
                #         center=cell_to_pixel_center(3, 3, self.offset_x)
                #     )
            break

        if self.state != State.PLAYING:
            return

        for gum in self.super_gums:
            if not gum.eated and (gum.x, gum.y) == (
                self.player.x,
                self.player.y,
            ):
                gum.eated = True
                self.player.score += self.p_p_s_p
                self.player.edible = True
                self.player.last_time_edible = self.now()
                break

    def check_win(self):
        if self.player.gums_eated < self.total_gums:
            return

        self.total_score += self.player.score
        self.level += 1

        if self.level == len(self.levels):
            self._end_run(True)
            # pygame.time.wait(3000)
        else:
            self._new_level()

    def _update_timer(self):
        self.time_left = self.level_time - (self.now() - self.level_start_time)
        if self.time_left <= 0:
            self.total_score += self.player.score
            self._end_run(False)

    def draw(self):
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

    def _draw_title(self, text="Pac Women", color="yellow", creator=False):
        """Draws the game title"""

        text_font = self._font("./fonts/pacfont/pac-font.ttf", 30)
        game_name = text_font.render(text, False, color)
        game_name_rect = game_name.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(game_name, game_name_rect)

        if creator:
            creator_font = self._font("./fonts/press/PressStart2P.ttf", 10)
            creator_font.set_italic(True)
            creator_name = creator_font.render(
                "jamourgh & aarid", False, color
            )
            creator_rect = creator_name.get_rect(
                center=(SCREEN_WIDTH // 2, 80)
            )
            self.screen.blit(creator_name, creator_rect)

    def _draw_menu(self):
        self.screen.fill((0, 0, 0))  # Clear screen with black background
        self._draw_title(creator=True)
        for btn in (
            self.play_btn,
            self.instructions_btn,
            self.leader_btn,
            self.exit_btn,
        ):
            btn.draw(self.screen)

    def _draw_instructions(self):
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
        text_font = self._font("./fonts/press/PressStart2P.ttf", 14)
        for i, line in enumerate(lines):
            surf = text_font.render(line, False, "white")
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 40))
            self.screen.blit(surf, rect)

        self.back_btn.draw(self.screen)

    def _draw_highscores(self):
        self.screen.fill((0, 0, 0))
        self._draw_title("Top Players")

        players = sorted(self._load_highscores(), key=lambda p: -p["score"])
        text_font = self._font("./fonts/press/PressStart2P.ttf", 14)

        if not players:
            surf = text_font.render(
                "No scores yet - be the first!", False, "white"
            )
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, 150))
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
                #     name_surf = text_font.render(str(player['username']), False, 'white')
                name_surf = text_font.render(
                    f"{idx + 1}- {player['username']}", False, color
                )
                score_surf = text_font.render(
                    str(player["score"]), False, color
                )
                self.screen.blit(
                    name_surf,
                    name_surf.get_rect(topleft=(200, 130 + idx * 30)),
                )
                self.screen.blit(
                    score_surf,
                    score_surf.get_rect(topleft=(500, 130 + idx * 30)),
                )

        self.back_btn.draw(self.screen)

    def _draw_enter_name(self):
        self.screen.fill((0, 0, 0))
        if self.last_run_won:
            self._draw_title("You Win!", "green")
        else:
            self._draw_title("Game Over", "red")

        text_font = self._font("./fonts/press/PressStart2P.ttf", 16)
        score_surf = text_font.render(
            f"Final score: {self.pending_score}", False, "white"
        )
        self.screen.blit(
            score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, 200))
        )

        prompt_surf = text_font.render("Enter your name:", False, "white")
        self.screen.blit(
            prompt_surf, prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, 230))
        )

        self.back_btn.rect = pygame.Rect(
            self.back_btn.x, 400, self.back_btn.width, self.back_btn.height
        )

        self.name_input.draw(self.screen)
        self.submit_btn.draw(self.screen)
        self.back_btn.draw(self.screen)

    def _draw_game(self):
        self.screen.fill((0, 0, 0))
        self._draw_title(creator=True)
        self._draw_level_info()

        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                self.drawing.draw_cell(
                    self.screen, cell, x, y, self.player.moves
                )

        for ghost in self.ghosts:
            ghost.draw(self.screen)
        for gum in self.super_gums:
            gum.draw(self.screen)
        self.player.draw(self.screen)

    def _draw_level_info(self):
        text_font = self._font("./fonts/press/PressStart2P.ttf", 12)
        score_surf = text_font.render(
            f"Score: {self.player.score}", False, "white"
        )
        timer_surf = text_font.render(
            f"Timer: {max(self.time_left, 0) // 1000}", False, "white"
        )
        lives_surf = text_font.render(f"Lives: {self.lives}", False, "white")
        level_surf = text_font.render(
            f"Level: {self.level + 1}/{len(self.levels)}", False, "white"
        )

        # pygame.draw.line(self.screen, 'white', (0, 170), (SCREEN_WIDTH, 170), 3)
        self.screen.blit(score_surf, score_surf.get_rect(topleft=(100, 130)))
        self.screen.blit(
            lives_surf, lives_surf.get_rect(topleft=(100 + 150, 130))
        )
        self.screen.blit(
            timer_surf, timer_surf.get_rect(topleft=(100 + 310, 130))
        )
        self.screen.blit(
            level_surf, level_surf.get_rect(topleft=(100 + 470, 130))
        )

    def _draw_pause_overlay(self):
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        text_font = self._font("./fonts/pacfont/pac-font.ttf", 40)
        text = text_font.render("Paused", False, "yellow")
        self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 150)))

        self.paus_btn.draw(self.screen)
        self.quit_to_menu_btn.draw(self.screen)

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    config = {
        "highscore_filename": "highscores.json",
        "level": [
            {"width": 23, "height": 14},
            {"width": 11, "height": 11},
        ],
        "lives": 3,
        "points_per_pacgum": 15,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "level_max_time": 90000,
    }
    # config: Parser = Parser('config.json').config

    Game(config).run()
