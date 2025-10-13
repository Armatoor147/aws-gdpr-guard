variable "my_ip" {
  description = "My public IP for SSH access"
  type        = string
}

variable "s3_bucket_prefix" {
  type    = string
  default = "aws-gdpr-guard-ec2-deployment-s3-bucket"
}