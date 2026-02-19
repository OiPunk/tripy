# Roadmap

## Current State (2026-02-19)

Tripy application-layer delivery is complete:

- Backend architecture, auth, RBAC, migrations, observability hooks
- Production-grade web console with bilingual UX (`en` / `zh`)
- Keyboard-accessible interaction model and quality gates
- CI checks for backend + frontend E2E accessibility audit

## Remaining Milestone

- Execute AWS deployment in target account and validate runtime traffic

## AWS Deployment Scope (Implemented)

- Terraform stack for networking, compute, and data tier (`infra/terraform/`)
- Container build/publish and rollout workflow (`.github/workflows/deploy-aws.yml`)
- Secrets management wiring, health probes, and ALB ingress
- Frontend static hosting deployment flow (S3 + CloudFront)
