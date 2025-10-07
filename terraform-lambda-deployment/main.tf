terraform {
    required_providers {
      aws = {
        source = "hashicorp/aws"
        version = "~> 5.0"
      }
    }
}

provider "aws" {
    region = "eu-north-1"
}


# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
    name = "aws_gdpr_guard_lambda_role"
    assume_role_policy = jsonencode({
        Version = "2012-10-17",
        Statement = [{
            Action = "sts:AssumeRole",
            Effect = "Allow",
            Principal = {
                Service = "lambda.amazonaws.com"
            }
        }]
    })
}

# IAM Policy for S3
resource "aws_iam_policy" "lambda_s3_policy" {
    name = "aws_gdpr_guard_lambda_s3_policy"
    description = "Read/Write/List access for S3"
    policy = jsonencode({
        Version = "2012-10-17",
        Statement = [{
            Effect = "Allow",
            Action = ["s3:GetObject", "s3:PutObject", "s3: ListBucket"],
            Resource = [
                "arn:aws:s3:::${local.bucket_name}",
                "arn:aws:s3:::${local.bucket_name}/*"
            ]
        }]
    })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
    role = aws_iam_role.lambda_role.name
    policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

# Create a temporary directory with the correct structure
resource "null_resource" "prepare_layer" {
  provisioner "local-exec" {
    command = <<EOT
      mkdir -p ${path.module}/layer/python/aws_gdpr_guard
      cp -r ${path.module}/../aws_gdpr_guard/* ${path.module}/layer/python/aws_gdpr_guard/
    EOT
  }
}

# Zip the custom library
data "archive_file" "gdpr_guard_layer" {
    depends_on  = [null_resource.prepare_layer]
    type        = "zip"
    source_dir  = "${path.module}/layer/"
    output_path = "${path.module}/aws_gdpr_guard_layer.zip"
}

# Create the Lambda layer
resource "aws_lambda_layer_version" "gdpr_guard_layer" {
    depends_on       = [data.archive_file.gdpr_guard_layer]
    layer_name          = "aws_gdpr_guard_layer"
    description         = "Obfuscator library"
    filename            = data.archive_file.gdpr_guard_layer.output_path
    compatible_runtimes = ["python3.12"]
    source_code_hash    = data.archive_file.gdpr_guard_layer.output_base64sha256
}

# Zip the Python file dynamically
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"
}

# Lambda function with Pandas layer
resource "aws_lambda_function" "lambda_function" {
    function_name = "aws-gdpr-guard-lambda"
    runtime = "python3.12"
    timeout = 60
    handler = "lambda_function.lambda_handler"
    role = aws_iam_role.lambda_role.arn
    #filename = "lambda_function.zip"
    filename = data.archive_file.lambda_zip.output_path
    layers = [
        "arn:aws:lambda:eu-north-1:336392948345:layer:AWSSDKPandas-Python312:2",
        aws_lambda_layer_version.gdpr_guard_layer.arn
    ]

    environment {
      variables = {
        S3_BUCKET_NAME = local.bucket_name
      }
    }
    source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}

# resource "aws_lambda_permission" "trigger" {
#     statement_id = "AllowExecutionFromS3Bucket"
#     action = "lambda:InvokeFunction"
#     function_name = aws_lambda_function.lambda_function.function_name
#     principal = "s3.amazonaws.com"
#     source_arn = "arn:aws:s3:::${local.bucket_name}"
# }

# Output the lambda ARN
output "lambda_arn" {
    value = aws_lambda_function.lambda_function
}

variable "S3_bucket_name" {
    type = string
    default = "vincent-toor-azorin-aws-gdpr-guard-test-bucket"
}

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