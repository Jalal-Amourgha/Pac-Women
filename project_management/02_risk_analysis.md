# Risk Analysis and Mitigation

## Risk Register

### High Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R01 | Type errors causing runtime crashes due to `None` values on game objects | High | High | Added runtime assertions before accessing potentially `None` attributes; Pydantic validation guards configuration inputs |
| R02 | Configuration file corruption or missing fields | Medium | High | Pydantic models with default values; pre-validation cleaning step strips invalid entries before model parsing |
| R03 | Maze generation producing unsolvable mazes | Low | Medium | DFS-based recursive backtracking guarantees a perfect maze (fully connected); BFS shortest path verification |

### Medium Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R04 | Ghost pathfinding performance degradation on large mazes | Low | Medium | BFS limited to grid-based pathfinding; ghosts recalculate each move cycle with speed throttling |
| R05 | Line-length violations from type ignore comments | Medium | Low | Line-length set to 79 in ruff config; `# type: ignore` used sparingly and kept short |
| R06 | Pygame dependency compatibility issues | Low | Medium | Pinned pygame version in pyproject.toml; isolated virtual environment via uv |

### Low Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R07 | Asset file loading failures (missing images) | Low | High | Graceful pygame error messages; assets bundled with project |
| R08 | Dual-player control conflicts | Low | Low | Separate control schemes (WASD vs Arrows/KJHL) verified in code |

## Resolved Risks

| ID | Risk | Resolution |
|----|------|------------|
| R09 | Linting failures from `.venv/` inclusion | Added `--exclude=.venv` to flake8 command in Makefile |
| R10 | `level_max_time` unit mismatch (seconds vs milliseconds) | Updated default from 90 to 90000 in validation.py; documentation corrected |
| R11 | Type annotation gaps on `buttons_map` dictionary | Added `# type: ignore` annotations on `.is_clicked()` calls and removed redundant `: Button` annotations |
