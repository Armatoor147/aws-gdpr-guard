# S3 bucket prefix
variable "s3_bucket_prefix" {
    type = string
    default = "aws-gdpr-guard-lambda-deployment-s3-bucket"
}

# AWS region
variable "aws_region" {
  description = "AWS region"
  type        = string
}