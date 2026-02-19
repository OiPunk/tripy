data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    },
    var.tags
  )

  web_bucket_name = var.web_bucket_name != "" ? var.web_bucket_name : "${local.name_prefix}-web-${data.aws_caller_identity.current.account_id}"

  jwt_secret = var.jwt_secret_key != "" ? var.jwt_secret_key : random_password.jwt_secret[0].result

  bootstrap_admin_password = var.bootstrap_admin_password != "" ? var.bootstrap_admin_password : random_password.bootstrap_admin_password[0].result

  cors_origins = jsonencode(distinct(compact(concat([
    "https://${aws_cloudfront_distribution.web.domain_name}"
  ], var.extra_cors_origins))))
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-vpc"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-igw"
  })
}

resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-${count.index + 1}"
    Tier = "public"
  })
}

resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-${count.index + 1}"
    Tier = "private"
  })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-rt"
  })
}

resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-nat-eip"
  })
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-nat"
  })

  depends_on = [aws_internet_gateway.main]
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-rt"
  })
}

resource "aws_route_table_association" "private" {
  count = length(aws_subnet.private)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "ALB ingress"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-sg"
  })
}

resource "aws_security_group" "ecs" {
  name        = "${local.name_prefix}-ecs-sg"
  description = "ECS service security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-sg"
  })
}

resource "aws_security_group" "db" {
  name        = "${local.name_prefix}-db-sg"
  description = "Database security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-sg"
  })
}

resource "aws_lb" "api" {
  name               = substr("${local.name_prefix}-alb", 0, 32)
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb"
  })
}

resource "aws_lb_target_group" "api" {
  name        = substr("${local.name_prefix}-api", 0, 32)
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id

  health_check {
    path                = "/api/v1/health/ready"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 20
    matcher             = "200"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-tg"
  })
}

resource "aws_lb_listener" "api_http" {
  load_balancer_arn = aws_lb.api.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

resource "aws_lb_listener" "api_https" {
  count = var.acm_certificate_arn != "" ? 1 : 0

  load_balancer_arn = aws_lb.api.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnets"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-subnets"
  })
}

resource "random_password" "db_password" {
  length  = 30
  special = true
}

resource "aws_db_instance" "main" {
  identifier             = "${local.name_prefix}-postgres"
  engine                 = "postgres"
  engine_version         = var.database_engine_version
  instance_class         = var.database_instance_class
  allocated_storage      = var.database_allocated_storage
  db_name                = var.database_name
  username               = var.database_username
  password               = random_password.db_password.result
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  publicly_accessible    = false
  multi_az               = false
  storage_encrypted      = true
  backup_retention_period = 7
  deletion_protection    = var.enable_deletion_protection
  skip_final_snapshot    = !var.enable_deletion_protection
  apply_immediately      = var.apply_immediately

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-postgres"
  })
}

resource "random_password" "jwt_secret" {
  count = var.jwt_secret_key == "" ? 1 : 0

  length  = 48
  special = true
}

resource "random_password" "bootstrap_admin_password" {
  count = var.bootstrap_admin_password == "" ? 1 : 0

  length  = 24
  special = true
}

resource "aws_secretsmanager_secret" "database" {
  name        = "${local.name_prefix}/tripy/database"
  description = "Tripy runtime database URL"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql+pg8000://${var.database_username}:${urlencode(random_password.db_password.result)}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${var.database_name}"
  })
}

resource "aws_secretsmanager_secret" "app" {
  name        = "${local.name_prefix}/tripy/app"
  description = "Tripy runtime app secrets"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    JWT_SECRET_KEY          = local.jwt_secret
    OPENAI_API_KEY          = var.openai_api_key
    BOOTSTRAP_ADMIN_PASSWORD = local.bootstrap_admin_password
  })
}

resource "aws_ecr_repository" "api" {
  name                 = "${local.name_prefix}-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-repo"
  })
}

resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire old images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 30
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${local.name_prefix}-ecs-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution_managed" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy_document" "ecs_execution_secrets" {
  statement {
    sid = "AllowReadTripySecrets"

    actions = [
      "secretsmanager:GetSecretValue",
      "kms:Decrypt"
    ]

    resources = [
      aws_secretsmanager_secret.database.arn,
      aws_secretsmanager_secret.app.arn
    ]
  }
}

resource "aws_iam_policy" "ecs_execution_secrets" {
  name   = "${local.name_prefix}-ecs-execution-secrets"
  policy = data.aws_iam_policy_document.ecs_execution_secrets.json

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution_secrets" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = aws_iam_policy.ecs_execution_secrets.arn
}

resource "aws_iam_role" "ecs_task" {
  name               = "${local.name_prefix}-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${local.name_prefix}/api"
  retention_in_days = 30

  tags = local.common_tags
}

resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = local.common_tags
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${local.name_prefix}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = tostring(var.task_cpu)
  memory                   = tostring(var.task_memory)
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "tripy-api"
      image     = var.api_image
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      command = ["sh", "-c", "alembic upgrade head && python main.py"]
      environment = [
        { name = "ENVIRONMENT", value = "production" },
        { name = "HOST", value = "0.0.0.0" },
        { name = "PORT", value = "8000" },
        { name = "API_V1_PREFIX", value = "/api/v1" },
        { name = "AUTO_CREATE_TABLES", value = "false" },
        { name = "LOG_JSON", value = "true" },
        { name = "CORS_ORIGINS", value = local.cors_origins },
        { name = "OPENAI_API_BASE", value = var.openai_api_base },
        { name = "LLM_MODEL", value = var.llm_model },
        { name = "GRAPH_ENABLED", value = tostring(var.graph_enabled) },
        { name = "OTEL_ENABLED", value = tostring(var.otel_enabled) },
        { name = "OTEL_SERVICE_NAME", value = "tripy-api" },
        { name = "OTEL_EXPORTER_OTLP_ENDPOINT", value = var.otel_exporter_otlp_endpoint },
        { name = "BOOTSTRAP_ADMIN_USERNAME", value = var.bootstrap_admin_username }
      ]
      secrets = [
        { name = "DATABASE_URL", valueFrom = "${aws_secretsmanager_secret.database.arn}:DATABASE_URL::" },
        { name = "JWT_SECRET_KEY", valueFrom = "${aws_secretsmanager_secret.app.arn}:JWT_SECRET_KEY::" },
        { name = "OPENAI_API_KEY", valueFrom = "${aws_secretsmanager_secret.app.arn}:OPENAI_API_KEY::" },
        { name = "BOOTSTRAP_ADMIN_PASSWORD", valueFrom = "${aws_secretsmanager_secret.app.arn}:BOOTSTRAP_ADMIN_PASSWORD::" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "api"
        }
      }
    }
  ])

  tags = local.common_tags
}

resource "aws_ecs_service" "api" {
  name            = "${local.name_prefix}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "tripy-api"
    container_port   = 8000
  }

  depends_on = [
    aws_lb_listener.api_http,
    aws_lb_listener.api_https
  ]

  tags = local.common_tags
}

resource "aws_s3_bucket" "web" {
  bucket        = local.web_bucket_name
  force_destroy = var.force_destroy_web_bucket

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-web"
  })
}

resource "aws_s3_bucket_public_access_block" "web" {
  bucket = aws_s3_bucket.web.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "web" {
  bucket = aws_s3_bucket.web.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_cloudfront_origin_access_control" "web" {
  name                              = "${local.name_prefix}-web-oac"
  description                       = "OAC for Tripy web bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "web" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name              = aws_s3_bucket.web.bucket_regional_domain_name
    origin_id                = "tripy-web-origin"
    origin_access_control_id = aws_cloudfront_origin_access_control.web.id
  }

  default_cache_behavior {
    target_origin_id       = "tripy-web-origin"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]
    compress               = true
    cache_policy_id        = "658327ea-f89d-4fab-a63d-7e88639e58f6"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-web-cdn"
  })
}

data "aws_iam_policy_document" "web_bucket_policy" {
  statement {
    sid = "AllowCloudFrontRead"

    actions = ["s3:GetObject"]

    resources = [
      "${aws_s3_bucket.web.arn}/*"
    ]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.web.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "web" {
  bucket = aws_s3_bucket.web.id
  policy = data.aws_iam_policy_document.web_bucket_policy.json
}
