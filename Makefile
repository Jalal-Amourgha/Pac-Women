install:
	uv run python3 -m pip install --upgrade pip
	uv sync
run:
	PYGAME_HIDE_SUPPORT_PROMPT= uv run python3 pac-man.py config.json

debug:
	python3 -m pdb uv run python3 pac-man.py config.json

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache

lint:
	flake8 . 
	mypy . --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs
