# Project Analysis and Associated Choices

## Project Overview

**Project Name:** Pac-Women  
**Curriculum:** 42  
**Developers:** jamourgh, aarid  
**Language:** Python 3.10.13  
**Framework:** Pygame  

## Project Description

Pac-Women is a Pac-Man clone featuring cooperative dual-player gameplay, procedural maze generation, and customizable configuration via JSON. Players navigate procedurally generated mazes consuming pellets while evading ghosts, with the ability to turn the tables using super gums.

## Key Technical Choices

### Language and Runtime

| Choice | Rationale |
|--------|-----------|
| Python 3.10.13 | Required by 42 curriculum; provides type hints and modern language features |
| uv | Fast Python package manager and resolver, replacing pip for dependency management |
| Pygame | Standard library for game rendering, input handling, and audio in Python |

### Architecture Decisions

| Choice | Rationale |
|--------|-----------|
| Modular OOP design | Each game entity (Player, Ghost, SuperGum, Drawing) is a separate class, promoting separation of concerns |
| State machine pattern | `State` enum controls game flow (MENU, PLAYING, PAUSED, etc.) for clean screen transitions |
| JSON configuration | Human-readable, lightweight, validated at runtime with Pydantic |
| Bitmask maze representation | Efficient cell encoding using bitwise operations for wall detection |
| Pydantic validation | Automatic type coercion and default fallback for configuration, preventing runtime crashes |

### Maze Generation

- **Algorithm:** Randomized recursive backtracking (DFS) with optional imperfect maze generation
- **42 Pattern:** Centered "42" stamp carved into the maze when dimensions allow (width >= 14 and height >= 14)
- **Shortest Path:** BFS pathfinder from entry to exit cell for informational purposes

### Ghost AI

- **Chase:** BFS-based pathfinding toward the closest player
- **Flee:** Move away from the player (Manhattan distance) when edible
- **Wander:** Random movement as fallback when no path is available

### Dual-Player Support

- P1: WASD controls
- P2: Arrow keys + KJHL

### Linting and Type Safety

| Tool | Purpose |
|------|---------|
| flake8 | PEP 8 compliance and basic static analysis |
| mypy | Strict static type checking |
| ruff | Code formatting rules (line-length = 79) |

## Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| Strict type checking with nullable attributes | Strategic use of `assert` and `# type: ignore` where runtime guarantees exist but type inference cannot follow |
| Configuration validation edge cases | Pydantic model validation with pre-cleaning step to strip None/negative values |
| Game crashes from null references | Runtime assertions and defensive coding patterns |
