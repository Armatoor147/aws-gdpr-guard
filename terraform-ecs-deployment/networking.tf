# Security group for the ECS service
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

# Default VPC
resource "aws_default_vpc" "default" {}


# Default subnets
resource "aws_default_subnet" "default" {
  count = 3
  availability_zone = "${var.aws_region}${count.index == 0 ? "a" : count.index == 1 ? "b" : "c"}"
}