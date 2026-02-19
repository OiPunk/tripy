# Tripy

[![CI](https://github.com/OiPunk/tripy/actions/workflows/ci.yml/badge.svg)](https://github.com/OiPunk/tripy/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](./pyproject.toml)
[![Release](https://img.shields.io/github/v/release/OiPunk/tripy?include_prereleases)](https://github.com/OiPunk/tripy/releases)
[![E2E](https://img.shields.io/badge/e2e-playwright-45ba63)](./web/e2e/tripy.spec.ts)

Tripy is an enterprise-grade, graph-native travel assistant platform built with FastAPI + LangGraph.
It provides secure auth, RBAC, migration-driven data management, observability hooks, and a production-ready web console.

## Delivery Status

- Application layer: complete (backend + frontend + CI quality gates)
- AWS deployment assets: complete (`infra/terraform` + `Deploy AWS` workflow)
- Remaining milestone: run deployment in target AWS account

## Why Tripy

- Production-first backend architecture (`src/` layout, typed schemas, migration workflow)
- Graph orchestration for travel workflows with interruption-aware execution
- RBAC model with permission gates for admin and graph execution
- OpenTelemetry integration (FastAPI, SQLAlchemy, logging)
- End-to-end tested web console with i18n (`en` / `zh`) and accessibility checks

## Feature Set

### Backend

- FastAPI app factory with API versioning (`/api/v1`)
- JWT authentication + user bootstrap
- Role/permission RBAC data model
- Alembic migrations and migration smoke validation
- Health probes (`/health/live`, `/health/ready`)
- LangGraph execution endpoint (`/graph/execute`)

### Frontend (`web/`)

- React + TypeScript + Vite console
- Graph assistant workspace (threaded conversation)
- Identity/RBAC inspector
- Admin user inventory page
- System health panel
- Runtime language switch (`en`, `zh`)
- Keyboard-accessible navigation + ARIA landmarks
- Playwright E2E + axe accessibility audit

## Architecture

```mermaid
flowchart TD
    client["Web Console"] --> api["FastAPI /api/v1"]
    api --> auth["Auth + RBAC"]
    api --> graph["Graph Service"]
    auth --> db["SQLAlchemy + Alembic"]
    graph --> legacy["Legacy LangGraph Toolchain"]
    api --> obs["OpenTelemetry"]
```

## Quick Start

### 1) Backend

```bash
git clone https://github.com/OiPunk/tripy.git
cd tripy
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
alembic upgrade head
python main.py
```

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2) Frontend

```bash
cd web
npm install
cp .env.example .env
npm run dev
```

- Web console: [http://127.0.0.1:4174](http://127.0.0.1:4174)

## Developer Workflow

### Backend quality gates

```bash
make lint
make format
make typecheck
make test
make migrate
```

### Frontend quality gates

```bash
make web-build
make web-test-e2e
```

## AWS Deployment

- Terraform stack: `infra/terraform`
- CI deployment workflow: `.github/workflows/deploy-aws.yml`
- Full guide: [`docs/AWS_DEPLOYMENT.md`](./docs/AWS_DEPLOYMENT.md)

## API Surface (Core)

- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/admin/users` (requires `users:read`)
- `POST /api/v1/graph/execute` (requires `graph:execute`)

## Repository Structure

```text
src/tripy/
  api/
  core/
  db/
  repositories/
  schemas/
  services/
web/
  src/
  e2e/
docs/
legacy:
  graph_chat/
  tools/
```

## Security Notes

- Keep secrets in environment variables only.
- Rotate `JWT_SECRET_KEY` before production.
- Keep `.env` and runtime data out of version control.
- Enforce permission gates for privileged APIs.

## Documentation

- [Architecture](./docs/ARCHITECTURE.md)
- [Development Guide](./docs/DEVELOPMENT.md)
- [API Notes](./docs/API.md)
- [Observability](./docs/OBSERVABILITY.md)
- [Frontend Contributing](./docs/FRONTEND_CONTRIBUTING.md)
- [UI Design Tokens](./docs/UI_DESIGN_TOKENS.md)
- [Roadmap](./docs/ROADMAP.md)
- [AWS Deployment](./docs/AWS_DEPLOYMENT.md)

## Open Source Standards

- [Contributing](./CONTRIBUTING.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Security Policy](./SECURITY.md)
- [Changelog](./CHANGELOG.md)
- [License](./LICENSE)
