# API Contract (v1)

## Health

- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`

## Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

`/api/v1/auth/login` returns JWT plus resolved role/permission lists.

## Admin

- `GET /api/v1/admin/users` (`users:read` permission required)

## Graph

- `POST /api/v1/graph/execute` (`graph:execute` permission required)

Headers for authenticated endpoints:

```http
Authorization: Bearer <access_token>
```
