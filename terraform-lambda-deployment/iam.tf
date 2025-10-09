# IAM Role for Lambda
resource "aws_iam_role" "lambda_iam_role" {
    name = "aws-gdpr-guard-lambda-role"
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

# IAM Policy for S3 access
resource "aws_iam_policy" "lambda_s3_policy" {
    name = "aws-gdpr-guard-lambda-s3-policy"
    description = "Read/Write/List access for S3"
    policy = jsonencode({
        Version = "2012-10-17",
        Statement = [{
            Effect = "Allow",
            Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
            Resource = [
                "arn:aws:s3:::${local.bucket_name}",
                "arn:aws:s3:::${local.bucket_name}/*"
            ]
        }]
    })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
    role = aws_iam_role.lambda_iam_role.name
    policy_arn = aws_iam_policy.lambda_s3_policy.arn
}