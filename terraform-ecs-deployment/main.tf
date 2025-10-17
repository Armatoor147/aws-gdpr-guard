terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Create an ECS cluster
resource "aws_ecs_cluster" "aws_gdpr_guard_cluster" {
  name = "aws-gdpr-guard-cluster"
}

# Create a task definition
resource "aws_ecs_task_definition" "gdpr_guard_task" {
  family                   = "aws-gdpr-guard-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([{
    name      = "aws-gdpr-guard-container"
    image     = "${var.ecr_repository_url}:latest"
    essential = true
    environment = [
      {
        name  = "AWS_DEFAULT_REGION"
        value = var.aws_region
      }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/aws-gdpr-guard-task"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

resource "aws_cloudwatch_log_group" "gdpr_guard_logs" {
  name = "/ecs/aws-gdpr-guard-task"
}

# Create an IAM role for ECS task execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "aws-gdpr-guard-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# Attach the AmazonECSTaskExecutionRolePolicy to the role
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Create an IAM role for the ECS task (to access S3)
resource "aws_iam_role" "ecs_task_role" {
  name = "aws-gdpr-guard-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# Attach a custom policy to allow S3 access
resource "aws_iam_role_policy" "ecs_task_s3_policy" {
  name = "aws-gdpr-guard-ecs-task-s3-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ]
      Resource = [
        "arn:aws:s3:::vincent-toor-azorin-aws-gdpr-guard-test-bucket",
        "arn:aws:s3:::vincent-toor-azorin-aws-gdpr-guard-test-bucket/*"
      ]
    }]
  })
}

# Create a security group for the ECS service
resource "aws_security_group" "ecs_service_sg" {
  name        = "aws-gdpr-guard-ecs-service-sg"
  description = "Allow outbound traffic for ECS service"
  vpc_id      = aws_default_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Use the default VPC
resource "aws_default_vpc" "default" {}

# Uncomment the "ECS service" resource to make the script run continuously
# Create an ECS service (automated manager for ECS tasks)
# resource "aws_ecs_service" "gdpr_guard_service" {
#   name            = "aws-gdpr-guard-service"
#   cluster         = aws_ecs_cluster.aws_gdpr_guard_cluster.id
#   task_definition = aws_ecs_task_definition.gdpr_guard_task.arn
#   desired_count   = 1
#   launch_type     = "FARGATE"

#   network_configuration {
#     subnets          = aws_default_subnet.default[*].id
#     security_groups  = [aws_security_group.ecs_service_sg.id]
#     assign_public_ip = true
#   }
# }

# Use the default subnets
resource "aws_default_subnet" "default" {
  count = 3
  availability_zone = "${var.aws_region}${count.index == 0 ? "a" : count.index == 1 ? "b" : "c"}"
}




variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}

variable "account_id" {
  description = "AWS account ID"
  type        = string
  default = "312596058192"
}

variable "ecr_repository_url" {
  description = "ECR repository URL"
  type        = string
}




output "ecs_cluster_name" {
  value = aws_ecs_cluster.aws_gdpr_guard_cluster.name
}

# output "ecs_service_name" {
#   value = aws_ecs_service.gdpr_guard_service.name
# }