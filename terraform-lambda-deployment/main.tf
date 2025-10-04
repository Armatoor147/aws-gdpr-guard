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
                "arn:aws:s3:::BUCKEY-NAME", # Replace BUCKET-NAME with a variable
                "arn:aws:s3:::BUCKET-NAME/*" # Replace BUCKET-NAME with a variable
            ]
        }]
    })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
    role = aws_iam_role.lambda_role.name
    policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

# Lambda function with Pandas layer
resource "aws_lambda_function" "lambda_function" {
    function_name = "aws-gdpr-guard-lambda"
    runtime = "python3.12"
    timeout = 60
    handler = "lambda_function.lambda_handler"
    role = aws_iam_role.lambda_role.arn

    filename = "X"

    layers = ["arn:aws:lambda:eu-north-1:336392948345:layer:AWSSDKPandas-Python312:2"]

    environment {
      variables = {
        BUCKET_NAME = "X"
      }
    }
}

# Output the lambda ARN
output "lambda_arn" {
    value = aws_lambda_function.lambda_function
}

