# Blocking Points and Conflicts

## Blocking Issues During Development

### 1. Strict Type Checking Incompatibility (Resolved)

**Description:** Enabling mypy with `--disallow-untyped-defs` and `--warn-return-any` revealed numerous type errors across the codebase. The `buttons_map` dictionary typed as `dict[str, Button | TextInput]` caused `is_clicked()` method access errors, and several attributes (`self.player`, `self.maze`, `self.drawing`) were typed as `None`-able but accessed without null checks in gameplay code paths.

**Impact:** High — blocked the linting phase from passing.

**Resolution:** Added `assert` statements to narrow `None`-able types at runtime, used `# type: ignore` annotations on dictionary lookups where the type was known to be `Button`, and removed redundant `: Button` type annotations in favor of letting mypy infer from context with appropriate ignores.

**Lesson:** Starting with stricter type annotations from the beginning would have reduced refactoring effort later.

### 2. Configuration Unit Mismatch (Resolved)

**Description:** The `level_max_time` field was defined with a default of `90` in the Pydantic model and documented as "in seconds" in the README, but the codebase treats it as milliseconds (comparing against `pygame.time.get_ticks()` return values). The `config.json` override set it to `90000`, revealing the inconsistency.

**Impact:** Medium — could cause confusion for users and incorrect gameplay timing if using the default.

**Resolution:** Updated the default to `90000` in `validation.py` and corrected the README documentation to specify milliseconds.

**Lesson:** Configuration field units must be explicitly documented and consistently used between the model and the consuming code.

### 3. Linting Scope Including Dependencies (Resolved)

**Description:** The initial `flake8 .` command analyzed all Python files including those in `.venv/`, producing thousands of false-positive linting errors from third-party packages like PyInstaller.

**Impact:** Medium — blocked the linting target from passing cleanly.

**Resolution:** Added `--exclude=.venv` flag to the flake8 command in the Makefile.

**Lesson:** Always scope linters to project source code, excluding virtual environments and dependency directories.

## Team Conflicts

### No Critical Conflicts

Both developers collaborated effectively throughout the project. Any design disagreements were resolved through discussion and alignment with project requirements. The 42 curriculum's strict standards (linting, type hints, documentation) served as an objective basis for code quality decisions, eliminating subjective disagreements.

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Blocking issues | 3 | All resolved |
| Team conflicts | 0 | None |
| Open items | 0 | All addressed |
