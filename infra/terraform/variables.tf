variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project identifier"
  type        = string
  default     = "tripy"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"
}

variable "api_image" {
  description = "Container image for API service"
  type        = string
  default     = "public.ecr.aws/docker/library/python:3.12-slim"
}

variable "api_desired_count" {
  description = "ECS desired task count"
  type        = number
  default     = 1
}

variable "task_cpu" {
  description = "Fargate task CPU units"
  type        = number
  default     = 512
}

variable "task_memory" {
  description = "Fargate task memory in MiB"
  type        = number
  default     = 1024
}

variable "vpc_cidr" {
  description = "VPC CIDR range"
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs"
  type        = list(string)
  default     = ["10.42.0.0/20", "10.42.16.0/20"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs"
  type        = list(string)
  default     = ["10.42.128.0/20", "10.42.144.0/20"]
}

variable "database_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "tripy"
}

variable "database_username" {
  description = "PostgreSQL database username"
  type        = string
  default     = "tripy"
}

variable "database_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "database_allocated_storage" {
  description = "RDS storage size (GB)"
  type        = number
  default     = 20
}

variable "database_engine_version" {
  description = "PostgreSQL major/minor version"
  type        = string
  default     = "16.3"
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for RDS"
  type        = bool
  default     = false
}

variable "apply_immediately" {
  description = "Apply RDS modifications immediately"
  type        = bool
  default     = true
}

variable "openai_api_key" {
  description = "OpenAI API key injected into runtime secrets"
  type        = string
  default     = "EMPTY"
  sensitive   = true
}

variable "openai_api_base" {
  description = "OpenAI-compatible API base URL"
  type        = string
  default     = "https://api.openai.com/v1"
}

variable "llm_model" {
  description = "Default LLM model name"
  type        = string
  default     = "gpt-4.1-mini"
}

variable "jwt_secret_key" {
  description = "JWT secret key; leave empty to auto-generate"
  type        = string
  default     = ""
  sensitive   = true
}

variable "bootstrap_admin_username" {
  description = "Initial admin username"
  type        = string
  default     = "admin"
}

variable "bootstrap_admin_password" {
  description = "Initial admin password; leave empty to auto-generate"
  type        = string
  default     = ""
  sensitive   = true
}

variable "graph_enabled" {
  description = "Enable graph execution endpoint"
  type        = bool
  default     = true
}

variable "otel_enabled" {
  description = "Enable OpenTelemetry in application"
  type        = bool
  default     = false
}

variable "otel_exporter_otlp_endpoint" {
  description = "OTLP endpoint for traces"
  type        = string
  default     = ""
}

variable "extra_cors_origins" {
  description = "Additional CORS origins beyond CloudFront domain"
  type        = list(string)
  default     = []
}

variable "acm_certificate_arn" {
  description = "Optional ACM cert ARN for HTTPS on ALB"
  type        = string
  default     = ""
}

variable "web_bucket_name" {
  description = "Optional custom S3 bucket name for web static assets"
  type        = string
  default     = ""
}

variable "force_destroy_web_bucket" {
  description = "Allow Terraform to delete non-empty web bucket"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
