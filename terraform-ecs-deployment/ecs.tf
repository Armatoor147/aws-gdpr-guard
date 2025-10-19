# ECS cluster
resource "aws_ecs_cluster" "aws_gdpr_guard_cluster" {
  name = "aws-gdpr-guard-cluster"
}

# Task definition
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
    image     = "${var.ecr_repository_uri}:latest"
    essential = true
    environment = [
      {
        name  = "AWS_DEFAULT_REGION"
        value = var.aws_region
      },
      {
        name  = "S3_BUCKET_NAME"
        value = local.bucket_name
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

# Cloudwatch log
resource "aws_cloudwatch_log_group" "gdpr_guard_logs" {
  name = "/ecs/aws-gdpr-guard-task"
}

# Uncomment the "ECS service" resource to make the script run continuously
# ECS service (automated manager for ECS tasks)
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