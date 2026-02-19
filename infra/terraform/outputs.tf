output "api_ecr_repository_url" {
  description = "ECR repository URL for Tripy API image"
  value       = aws_ecr_repository.api.repository_url
}

output "api_alb_dns_name" {
  description = "Public DNS of API ALB"
  value       = aws_lb.api.dns_name
}

output "api_base_url" {
  description = "Base URL for API ingress"
  value       = var.acm_certificate_arn != "" ? "https://${aws_lb.api.dns_name}" : "http://${aws_lb.api.dns_name}"
}

output "web_bucket_name" {
  description = "S3 bucket that stores built frontend assets"
  value       = aws_s3_bucket.web.bucket
}

output "web_cloudfront_distribution_id" {
  description = "CloudFront distribution ID for web frontend"
  value       = aws_cloudfront_distribution.web.id
}

output "web_url" {
  description = "CloudFront URL for web frontend"
  value       = "https://${aws_cloudfront_distribution.web.domain_name}"
}

output "database_secret_arn" {
  description = "Secret ARN containing DATABASE_URL"
  value       = aws_secretsmanager_secret.database.arn
}

output "app_secret_arn" {
  description = "Secret ARN containing app secrets (JWT/OpenAI/Admin password)"
  value       = aws_secretsmanager_secret.app.arn
}

output "bootstrap_admin_username" {
  description = "Bootstrap admin username configured for runtime"
  value       = var.bootstrap_admin_username
}
