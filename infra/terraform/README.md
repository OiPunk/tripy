# Tripy AWS Terraform

This stack provisions production-ready AWS infrastructure for Tripy:

- VPC (public + private subnets, NAT)
- ECS Fargate API service behind ALB
- PostgreSQL RDS instance
- ECR repository for API image
- Secrets Manager entries for runtime secrets
- S3 + CloudFront for frontend static hosting
- CloudWatch log group and IAM roles

## Prerequisites

- Terraform >= 1.6
- AWS account with IAM permissions for VPC, ECS, RDS, ECR, IAM, S3, CloudFront, Secrets Manager
- Docker (for building API image)

## Quick Start

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply -target=aws_ecr_repository.api -auto-approve
```

Push API image:

```bash
ECR_REPO=$(terraform output -raw api_ecr_repository_url)

aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin "${ECR_REPO%/*}"

docker build -t "$ECR_REPO:latest" .
docker push "$ECR_REPO:latest"
```

Run full apply with the pushed image:

```bash
terraform apply -auto-approve -var "api_image=${ECR_REPO}:latest"
```

Deploy frontend assets:

```bash
WEB_BUCKET=$(terraform output -raw web_bucket_name)
DIST_ID=$(terraform output -raw web_cloudfront_distribution_id)
API_BASE=$(terraform output -raw api_base_url)

cd ../../web
VITE_API_BASE="${API_BASE}/api/v1" npm ci
VITE_API_BASE="${API_BASE}/api/v1" npm run build

aws s3 sync dist "s3://${WEB_BUCKET}" --delete
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*"
```

## Notes

- ECS task runs migrations on startup (`alembic upgrade head`).
- Runtime secrets are stored in Secrets Manager.
- CloudFront domain is automatically added to backend CORS origins.
