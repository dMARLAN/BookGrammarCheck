.PHONY: dev-install install format lint test run

SHELL := "bash"
ACTIVATE := "." ".venv/Scripts/activate"

dev-install:
	@bash -c "$(ACTIVATE) && pip install -qqqr ./src/dev-requirements.txt"

install:
	@bash -c "$(ACTIVATE) && pip install -qqqr ./src/requirements.txt"

format: dev-install
	@bash -c "$(ACTIVATE) && black --line-length=120 ./src"

lint: dev-install
	@bash -c "$(ACTIVATE) && ruff check . && pyright ./src"

test: dev-install
	@bash -c "$(ACTIVATE) && pytest ./tests"

run: install
	@bash -c "$(ACTIVATE) && winpty python ./src/main.py"
