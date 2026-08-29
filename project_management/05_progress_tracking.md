# Progress Tracking

## Actual Progress vs. Plan

The project followed an iterative development approach, with each git commit representing a completed, tested feature. Below is the progress tracking based on the commit history.

## Commit Log (Chronological)

| Commit | Description | Phase |
|--------|-------------|-------|
| Initial setup | Project structure, pyproject.toml | Phase 1 |
| UP | Core game logic and entity classes | Phase 2 |
| Fix: most linting | Type hints and flake8 compliance | Phase 2 |
| Add: second player re-spawn cell | Dual-player respawn | Phase 4 |
| Fix: levels size | Level configuration adjustments | Phase 5 |
| Fix: Buttons quit/back collusion | UI bug fixes | Phase 4 |
| Fix pip upgrade cmd | Makefile dependency management | Phase 5 |
| Add: README | Project documentation | Phase 8 |
| Add: Pacman eat ghost sound | Audio implementation | Phase 6 |
| UP: Matchup | Game balance and alignment | Phase 6 |
| UP | General improvements | Phase 6 |
| Add: spec file for PyInstaller | Packaging configuration | Phase 8 |
| Handle and detect if program is executed as bundle | Bundled executable support | Phase 8 |
| Clean some unused assets | Asset optimization | Phase 8 |
| Add: quick minimal in-package instructions | In-game instructions | Phase 6 |
| Clean the scores file for a fresh start | Data management fix | Phase 6 |
| Fix: a mis default value | Configuration default correction | Phase 5 |
| feat: README UP | Documentation update | Phase 8 |
| feat: Fix linting | Linting compliance | Phase 7 |
| Add: bundled executable self independent file | Final packaging | Phase 8 |

## Milestone Achievement

| Milestone | Target | Actual |
|-----------|--------|--------|
| All features implemented | Sprint end | On track |
| Linting passes (`make lint`) | Before delivery | Complete |
| Executable build | Before delivery | Complete |
| Documentation | Before delivery | Complete |

## Deviation Notes

- **Configuration defaults:** `level_max_time` default was corrected from 90 to 90000 during development, reflecting a unit mismatch that was caught during testing
- **Linting scope:** Initially `flake8 .` included `.venv/` dependencies, requiring an `--exclude=.venv` fix — this was identified and resolved during the linting phase
- **Type safety:** Strict mypy mode revealed multiple `None`-related type issues that were resolved with assertions and `# type: ignore` annotations
