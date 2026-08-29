# Team Organization

## Team Members

| Name | Role | Responsibilities |
|------|------|-----------------|
| jamourgh | Developer | Core game logic, maze generation, ghost AI, README documentation |
| aarid | Developer | UI/UX (menus, buttons), configuration system, validation, dual-player mode |

## Decision-Making Process

- **Pair programming:** Both developers collaborated on all features; decisions were made through discussion and code review
- **Code style:** PEP 8 compliance enforced via flake8; type hints required across all files via mypy
- **Line length:** 79 characters (42 standard), enforced by ruff configuration
- **Git workflow:** Direct commits to main branch with descriptive commit messages following conventional commits style

## Task Distribution

### jamourgh

- Game state machine and event handling (`pac-man.py`)
- Maze generator (`mazegenerator/`)
- Ghost AI and movement (`ghost.py`)
- Super gum mechanics (`superGum.py`)
- README and project documentation

### aarid

- UI widgets (`button.py`, `text.py`)
- Drawing and rendering (`drawing.py`)
- Configuration validation (`validation.py`)
- Utility functions (`utils.py`)
- Custom print helpers (`custom_print.py`)

## Communication

- Daily sync on progress and blockers
- Shared code repository for real-time collaboration
- TODO.md maintained during active development for task tracking

## Conflict Resolution

- Code conflicts resolved through direct discussion and mutual agreement
- Type safety and linting standards were non-negotiable — all code must pass `make lint`
- Feature disagreements settled by evaluating the simplest implementation that satisfies requirements
