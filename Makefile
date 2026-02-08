PYTHON ?= python3
PIP ?= pip3

.PHONY: install install-dev run lint format typecheck test clean precommit migrate downgrade web-install web-dev web-build web-test-e2e

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e .[dev]

run:
	$(PYTHON) main.py

lint:
	ruff check src tests

format:
	ruff format src tests

typecheck:
	mypy src/tripy

test:
	pytest

precommit:
	pre-commit run --all-files

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade -1

web-install:
	cd web && npm install

web-dev:
	cd web && npm run dev

web-build:
	cd web && npm run build

web-test-e2e:
	cd web && npm run test:e2e

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
