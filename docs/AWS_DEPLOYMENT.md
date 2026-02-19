# AWS Deployment Guide

Tripy is now wired for AWS delivery with Terraform + GitHub Actions.

## What Is Provisioned

- Networking: VPC, subnets, NAT, security groups
- Compute: ECS Fargate service + ALB
- Data: PostgreSQL RDS
- Registry: ECR API repository
- Secrets: Secrets Manager for runtime credentials
- Frontend hosting: S3 + CloudFront
- Observability baseline: CloudWatch logs for API containers

## Files

- `infra/terraform/` - infrastructure as code
- `.github/workflows/deploy-aws.yml` - one-click CI deployment workflow

## GitHub Requirements

Repository secrets:

- `AWS_DEPLOY_ROLE_ARN` (OIDC assumable role)
- `OPENAI_API_KEY` (optional; defaults to `EMPTY`)
- `JWT_SECRET_KEY` (optional; auto-generated if omitted)
- `BOOTSTRAP_ADMIN_PASSWORD` (optional; auto-generated if omitted)

Repository variables:

- `AWS_REGION` (optional, default `us-east-1`)
- `ACM_CERTIFICATE_ARN` (optional for HTTPS ALB listener)
- `EXTRA_CORS_ORIGINS_JSON` (optional JSON array string, e.g. `[
  "https://app.example.com"
]`)

## Deploy (GitHub)

1. Trigger `Deploy AWS` workflow.
2. Optionally provide `image_tag`.
3. Wait for workflow completion.
4. Workflow outputs API base URL and web URL.

## Deploy (Local)

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply -target=aws_ecr_repository.api -auto-approve

ECR_REPO=$(terraform output -raw api_ecr_repository_url)
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin "${ECR_REPO%/*}"

docker build -t "$ECR_REPO:latest" .
docker push "$ECR_REPO:latest"

terraform apply -auto-approve -var "api_image=${ECR_REPO}:latest"

WEB_BUCKET=$(terraform output -raw web_bucket_name)
DIST_ID=$(terraform output -raw web_cloudfront_distribution_id)
API_BASE=$(terraform output -raw api_base_url)

cd ../../web
VITE_API_BASE="${API_BASE}/api/v1" npm ci
VITE_API_BASE="${API_BASE}/api/v1" npm run build
aws s3 sync dist "s3://${WEB_BUCKET}" --delete
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*"
```

## Runtime Notes

- ECS task runs `alembic upgrade head` before starting the API server.
- `AUTO_CREATE_TABLES` is forced to `false` in production task definition.
- CloudFront domain is injected into API CORS origins automatically.
