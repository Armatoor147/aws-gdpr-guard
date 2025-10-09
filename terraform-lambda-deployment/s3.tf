# Create the S3 bucket
resource "aws_s3_bucket" "aws_gdpr_guard_bucket" {
    bucket = local.bucket_name
}

# Upload dummy CSV
resource "aws_s3_object" "dummy_students" {
    bucket = aws_s3_bucket.aws_gdpr_guard_bucket.bucket
    key = "dummy_students.csv"
    source = "${path.module}/../dummy_data/dummy_students.csv"
    content_type = "text/csv"
}