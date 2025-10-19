# Local IP address
variable "my_ip" {
  description = "My public IP for SSH access"
  type        = string
}

# S3 bucket prefix
variable "s3_bucket_prefix" {
  type    = string
  default = "aws-gdpr-guard-ec2-deployment-s3-bucket"
}

# AWS region
variable "aws_region" {
  description = "AWS region"
  type        = string
}