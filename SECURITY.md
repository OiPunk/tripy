# Security Policy

## Supported Versions

Only the latest version on `main` is actively maintained.

## Reporting a Vulnerability

Please report vulnerabilities privately by opening a security advisory in your Git hosting platform.
Include:

- Affected component and version
- Reproduction steps
- Potential impact
- Suggested remediation if available

Do not disclose zero-day details publicly before maintainers confirm and patch.

## Security Baseline

- Secrets must come from environment variables.
- Authentication is JWT bearer-based.
- RBAC permissions protect privileged API surfaces.
- Sensitive graph actions require an explicit confirmation flow.
- CI includes static checks and tests before merges.
