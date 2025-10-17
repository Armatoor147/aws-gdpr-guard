# S3 Bucket
resource "aws_s3_bucket" "aws_gdpr_guard_bucket" {
  bucket = local.bucket_name
}

# Upload dummy CSV
resource "aws_s3_object" "dummy_students_csv" {
  bucket       = aws_s3_bucket.aws_gdpr_guard_bucket.bucket
  key          = "dummy_students.csv"
  source       = "${path.module}/../dummy_data/dummy_students.csv"
  content_type = "text/csv"
}

# Upload dummy JSON
resource "aws_s3_object" "dummy_students_json" {
  bucket       = aws_s3_bucket.aws_gdpr_guard_bucket.bucket
  key          = "dummy_students.json"
  source       = "${path.module}/../dummy_data/dummy_students.json"
  content_type = "application/json"
}

# Upload dummy Parquet
resource "aws_s3_object" "dummy_students_parquet" {
  bucket       = aws_s3_bucket.aws_gdpr_guard_bucket.bucket
  key          = "dummy_students.parquet"
  source       = "${path.module}/../dummy_data/dummy_students.parquet"
  content_type = "application/octet-stream"
}