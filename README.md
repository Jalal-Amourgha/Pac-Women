_This project has been created as part of the 42 curriculum by jamourgh and aarid._

## Description

Pac-Women is a modern, feature-rich Pac-Man clone built using Python and Pygame. The game pays homage to the classic arcade mechanics while introducing cooperative dual-player gameplay, dynamic procedural maze generation, and customizable configuration.

The goal of the project is to provide an engaging arcade experience where players navigate through procedurally generated mazes to consume all pacgums (pellets) while evading active enemy ghosts. Players can turn the tables by eating super gums, making the ghosts edible and vulnerable to being eaten for bonus points.

## Instructions

### Requirements

To compile and run this project, you need:

- Python 3.10 or newer
- uv (a fast Python package installer and resolver) or pip
- Pygame library

### Installation

You can easily set up the project and install all required dependencies using the provided Makefile:

```bash
make install
```

This command will upgrade pip, sync dependencies, and prepare the local virtual environment (.venv) via uv.

### Execution

To launch the game, run:

```bash
make run
```

Alternatively, you can run it manually by specifying the configuration file:

```bash
uv run python3 pac-man.py config.json
```

### Debugging and Linting

- To run with the Python debugger (pdb):
  ```bash
  make debug
  ```
- To run static code analysis and linting (Mypy type checking and Flake8 compliance):
  ```bash
  make lint
  ```
- To clean up temporary cache files:
  ```bash
  make clean
  ```

## Resources

- **Pygame Documentation:** Official documentation for Pygame module features, surface drawing, event handling, and mixer sound control.
- **Pydantic Documentation:** Technical references for BaseModel-based validation schemas.
- **Breadth-First Search (BFS) Algorithms:** Articles and tutorials on finding shortest paths in grids/graphs, which is used for both ghost pathfinding and finding the shortest path in generated mazes.
- **Classic Arcade Pac-Man Design:** Documentation of original arcade mechanics, ghost movement styles, and edible timer rules.

### AI Usage Disclosure

Generative AI was used to assist in the development and refinement of this project:

- **Core:** Assisted in identifying game-crashing bugs
- **Type Hinting and Static Typing:** Assisted in adding strict type hints to function signatures and return types across the files
- **Comprehensive Documentation:** Assisted in drafting standardized docstrings for classes and methods where they were missing or empty.

## Configuration

The game's behavior, maps, and player details are fully customizable via a JSON configuration file (config.json). The schema is strictly validated at runtime using validation.py (with Pydantic):

- **window**: Configures global variables for seed control.
  - seed (NonNegativeInt, default 42): Seed for random number generator.
  - pacgum (NonNegativeInt, default 42): Seed for pacgums generation.
- **player**: Controls player limits and rewards.
  - lives (NonNegativeInt, default 3): Number of starting lives.
  - points_per_ghost (NonNegativeInt, default 200): Points rewarded for eating an edible ghost.
  - points_per_pacgum (NonNegativeInt, default 15): Points rewarded per standard pellet.
  - points_per_super_pacgum (NonNegativeInt, default 50): Points rewarded for super gums.
  - highscore_filename (str, default "highscores.json"): Path to load and store high scores.
  - level_max_time (NonNegativeInt, default 90000): Time limit for each level (in milliseconds).
- **maps**: A list of maps representing game levels.
  - Each map configures width (NonNegativeInt, default 23) and height (NonNegativeInt, default 14).

## Highscore

The highscore system allows players to track and submit their scores at the end of each run.

- **How it works:** High scores are persisted in a local JSON file (highscores.json by default). When a player finishes a run (either by winning all levels or losing all lives), they are prompted to input their name. The name and final score are appended to the list, which is then dynamically sorted in descending order of score. The top 10 players are rendered on the "High Scorers" leaderboard screen.
- **Implementation Choice:** A file-based JSON storage was chosen because it is lightweight, human-readable, requires zero external database installation, and easily fits the scope of a portable arcade game. It allows players to immediately see their ranks without setup overhead.

## Maze Generation

Maze generation is handled by the custom mazegenerator package located in ./mazegenerator/:

- **The A-Maze-ing Package:** It generates perfect or imperfect mazes on a grid of any given dimensions using a randomized Depth-First Search (DFS) / recursive backtracking algorithm.
- **42 Curriculum Pattern:** If the dimensions of the maze allow it (width >= 14 and height >= 14), a custom, centered "42" pattern (a stamp representing the 42 curriculum) is carved into the empty maze grid as obstacle blocks (fully enclosed wall cells of value 15).
- **Shortest Path Computation:** The generator uses a Breadth-First Search (BFS) pathfinder to automatically determine the shortest path from the entry cell to the exit cell of the maze.

## Implementation

The Pac-Women codebase is written entirely in Python, utilizing standard object-oriented design and pygame for rendering, input handling, and audio:

- **Game State Machine:** Handled by State enumeration (MENU, INSTRUCTIONS, HIGHSCORES, PLAYING, PAUSED, ENTER_NAME) to seamlessly switch screens.
- **Procedural Level Flow:** As players complete levels, the game automatically rebuilds the maze with increasing or decreasing dimensions, loads fresh sprites, and resets ghost/player coordinates.
- **Cooperative Mode:** Supports both single-player and co-op dual-player modes. P1 uses WASD keyboard controls, while P2 uses Arrows/KJHL.
- **Pydantic Validation Guard:** Before launching, validation.py cleans and validates the configuration payload, falling back to default values for missing or corrupted entries to prevent runtime crashes.

## General Software Architecture

The codebase is structured modularly:

- **Game class (pac-man.py):** The orchestrator of the entire lifecycle. Initializes Pygame surfaces, handles event polling, processes updates, triggers collision checks, plays sounds, and handles state transitions.
- **Player class (player.py):** Inherits from pygame.sprite.Sprite. Manages coordinates, keyboard controls, sprite animation frames (mouth open/closed, rotation based on direction), score increments, and tracks visited coordinates to prevent re-eating pellets.
- **Ghost class (ghost.py):** Represents the enemy ghosts. Implements chase behaviors targeting players via BFS, a fleeing behavior when edible, and a random wander fallback.
- **SuperGum class (superGum.py):** Represents super gums placed at the four corners of the maze that grant the players temporary edible power.
- **Drawing class (drawing.py):** Decodes the cell bitmasks (e.g. wall bits 1, 2, 4, 8) and draws the maze walls and standard pellets on the Pygame surface.
- **Button (button.py) & TextInput (text.py):** Reusable UI widgets for menu selection, click detection, hovering visual feedback, and text field inputs with blinking cursors.
- **utils.py:** Holds cross-module constants, speed limits, and core helper functions like grid collision checks (can_move) and screen positioning calculations (cell_to_pixel_center).

## Project Management

The progress and roadmap of the project were tracked using a localized, plain-text task board.

- **How we managed:** All developer features, linter goals, deadlines, and bugs were listed and updated in a TODO.md file during development, which helped the dev to manage the work.
