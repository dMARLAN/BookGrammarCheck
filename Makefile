.PHONY: dev-install install format lint run

dev-install:
	pip install -r ./src/dev-requirements.txt

install:
	pip install -r ./src/requirements.txt

format: dev-install
	black --line-length=120 ./src

lint: dev-install
	ruff check . && pyright ./src

run: install
	winpty python ./src/main.py
