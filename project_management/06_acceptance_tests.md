# Acceptance Test Plan

## Test Strategy

All features are validated through manual gameplay testing and automated linting. The acceptance criteria below cover all core features.

## Feature Test Matrix

### 1. Game Launch and Configuration

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Launch with default config | Run `make run` | Game starts with config.json settings | Pass |
| Launch with custom config | Run `python3 pac-man.py <custom_config>.json` | Game loads custom configuration | Pass |
| Missing config file | Remove config.json | Falls back to defaults, no crash | Pass |
| Invalid config values | Provide negative or null values in config | Pydantic strips invalid values, uses defaults | Pass |

### 2. Main Menu

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Menu navigation | Click buttons with mouse | Buttons respond with hover effect | Pass |
| Start Game click | Click "Start Game" button | Game transitions to PLAYING state | Pass |
| Dual Playing click | Click "Dual Playing" button | Game starts in dual-player mode | Pass |
| How To Play click | Click "How To Play" button | Instructions screen displayed | Pass |
| High Scorers click | Click "High Scorers" button | Leaderboard screen displayed | Pass |

### 3. Single Player Gameplay

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Player movement | Press WASD or Arrow keys | Pac-Man moves in the correct direction | Pass |
| Pellet consumption | Move over pellets | Score increments, pellet disappears | Pass |
| Ghost chase | Move near ghost | Ghost follows player via BFS pathfinding | Pass |
| Ghost flee | Eat super gum | Ghosts turn edible and flee | Pass |
| Level completion | Eat all pellets | Game advances to next level | Pass |

### 4. Dual-Player Mode

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| P1 controls | Press WASD | Player 1 moves correctly | Pass |
| P2 controls | Press Arrows/KJHL | Player 2 moves correctly | Pass |
| Independent movement | Both players move simultaneously | Each player moves independently | Pass |

### 5. Pause and Resume

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Pause during gameplay | Press ESC or click pause button | Game pauses, PAUSED state displayed | Pass |
| Resume from pause | Press ESC or click resume button | Game resumes from same state | Pass |

### 6. Game Over and Highscores

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Lose a life | Ghost catches player | Life lost, player respawns | Pass |
| Game over | All lives lost | Enter name screen displayed | Pass |
| Score submission | Enter name, submit | Score saved to highscores.json | Pass |
| Highscore sorting | Multiple games played | Scores displayed in descending order | Pass |

### 7. Cheat Codes (Ctrl+1 to Ctrl+7)

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Ctrl+1 | Toggle invisibility | Player becomes invisible/toggle | Pass |
| Ctrl+2 | Toggle ghost freeze | Ghosts freeze/unfreeze | Pass |
| Ctrl+3 | Decrease player speed | Player speed reduces (min 10) | Pass |
| Ctrl+4 | Skip level | Gum count increases, win check triggered | Pass |
| Ctrl+5 | Add 1000 points | Score increases by 1000 | Pass |
| Ctrl+6 | Set lives to infinity | Lives set to infinite | Pass |
| Ctrl+7 | Toggle time stop | Timer pauses/resumes | Pass |

### 8. Linting and Type Checking

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| flake8 compliance | Run `make lint` | No style violations | Pass |
| mypy strict mode | Run `make lint` | No type errors | Pass |
| Exclude .venv | Run `make lint` | Third-party packages not analyzed | Pass |

## Known Bugs Fixed

| Bug | Fix |
|-----|-----|
| `level_max_time` unit mismatch (seconds vs ms) | Changed default to 90000 milliseconds |
| Linting included `.venv/` dependencies | Added `--exclude=.venv` to flake8 |
| Type errors on nullable attributes | Added assertions and `# type: ignore` annotations |
| Button collision detection fix | Fixed quit/back button interaction |
| Second player respawn position | Fixed cell positioning on respawn |
