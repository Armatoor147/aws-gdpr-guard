variable "S3_bucket_prefix" {
    type = string
    default = "aws-gdpr-guard-bucket"
}

resource "random_id" "S3_bucket_suffix" {
    byte_length = 4
}

locals {
    bucket_name = "${var.S3_bucket_prefix}-${random_id.S3_bucket_suffix.hex}"
}

resource "aws_s3_bucket" "aws_gdpr_guard_bucket" {
    bucket = local.bucket_name
}

resource "aws_s3_object" "dummy_students" {
    bucket = aws_s3_bucket.aws_gdpr_guard_bucket.bucket
    key = "dummy_students.csv"
    source = "${path.module}/../dummy_data/dummy_students.csv"
    content_type = "text/csv"
}