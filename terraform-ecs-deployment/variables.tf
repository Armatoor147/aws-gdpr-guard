# S3 bucket prefix
variable "s3_bucket_prefix" {
    type = string
    default = "aws-gdpr-guard-ecs-deployment-s3-bucket"
}

# AWS region
variable "aws_region" {
  description = "AWS region"
  type        = string
}

# Account ID
variable "account_id" {
  description = "AWS account ID"
  type        = string
}

# ECR repository URI
variable "ecr_repository_uri" {
  description = "ECR repository URI"
  type        = string
}