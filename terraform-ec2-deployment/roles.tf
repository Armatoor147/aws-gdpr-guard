resource "aws_iam_role" "aws_gdpr_guard-EC2-IAM-role" {
    name = "aws_gdpr_guard-EC2-IAM-role"
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

resource "aws_iam_policy" "EC2-S3-policy" {
    name = "aws_gdpr_guard_EC2-S3-policy"
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

resource "aws_iam_role_policy_attachment" "EC2-S3-attach" {
  role       = aws_iam_role.aws_gdpr_guard-EC2-IAM-role.name
  policy_arn = aws_iam_policy.EC2-S3-policy.arn
}

# variable "S3_bucket_name" {
#     type = string
#     default = "vincent-toor-azorin-aws-gdpr-guard-test-bucket"
# }