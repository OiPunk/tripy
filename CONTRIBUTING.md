# Contributing Guide

## Development Setup

1. Create a Python virtual environment.
2. Install dependencies:

```bash
pip install -e .[dev]
```

3. Copy environment template:

```bash
cp .env.example .env
```

4. Start the service:

```bash
python main.py
```

## Quality Gates

Run these before pushing:

```bash
ruff check src tests
ruff format src tests
mypy src/tripy
pytest
```

Or use Makefile shortcuts:

```bash
make lint
make format
make typecheck
make test
make migrate
```

## Pull Requests

- Keep PRs focused and small.
- Include tests for behavior changes.
- Update docs when interfaces or configuration change.
- Do not commit secrets or local `.env` files.
