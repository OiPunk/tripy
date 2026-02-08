# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-02-08

### Added
- Project identity renamed to `tripy` with compatibility bridge for `ctrip_assistant` imports.
- Alembic migration system with initial schema (`users`, `roles`, `permissions`, RBAC link tables).
- RBAC authorization dependencies and protected admin endpoint (`/api/v1/admin/users`).
- OpenTelemetry integration for FastAPI and SQLAlchemy (OTLP + console exporter options).
- Graph API end-to-end test coverage (auth + interrupt + confirmation flow).

### Changed
- User auth responses now include resolved role and permission lists.
- Bootstrap process now seeds default RBAC model and enforces deterministic admin credentials.

## [0.1.0] - 2026-02-07

### Added
- Modern `src/`-based architecture with FastAPI app factory.
- Pydantic Settings based configuration and `.env`-driven secrets.
- JWT authentication endpoints (`/api/v1/auth/*`) and user bootstrap.
- Health endpoints (`/api/v1/health/live`, `/api/v1/health/ready`).
- Graph execution API adapter (`/api/v1/graph/execute`).
- Request ID middleware and standardized exception wiring.
- Tooling stack: Ruff, mypy, pytest, pre-commit, GitHub Actions.
- Containerization assets: Dockerfile and docker-compose.
- Open-source governance docs (CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, LICENSE).

### Changed
- Removed hardcoded API keys from legacy model integrations.
- Hardened legacy graph schemas and OAuth helper behavior.
- Improved fallback behavior for policy retriever (offline-safe embeddings fallback).

### Fixed
- Corrected SQLite file path formatting bug in legacy tools module.
- Fixed location transform handling for `None` inputs.
