# IAM role
resource "aws_iam_role" "aws_gdpr_guard_ec2_iam_role" {
  name = "aws-gdpr-guard-ec2-iam-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy
resource "aws_iam_policy" "aws_gdpr_guard_ec2_s3_policy" {
  name        = "aws-gdpr-guard-ec2-s3-policy"
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

# Attachment of IAM role and IAM policy
resource "aws_iam_role_policy_attachment" "EC2_S3_attach" {
  role       = aws_iam_role.aws_gdpr_guard_ec2_iam_role.name
  policy_arn = aws_iam_policy.aws_gdpr_guard_ec2_s3_policy.arn
}