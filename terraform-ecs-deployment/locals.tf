# Random 4-digit ID
resource "random_id" "s3_bucket_suffix" {
  byte_length = 4
}

# Assemble full S3 bucket name
locals {
  bucket_name = "${var.s3_bucket_prefix}-${random_id.s3_bucket_suffix.hex}"
}