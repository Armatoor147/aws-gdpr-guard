# Prepare the Lambda layer directory
resource "null_resource" "prepare_layer" {
    provisioner "local-exec" {
        command = <<EOT
            mkdir -p ${path.module}/layer/python/aws_gdpr_guard
            cp -r ${path.module}/../aws_gdpr_guard/* ${path.module}/layer/python/aws_gdpr_guard/
        EOT
    }
}

# Zip the custom library
data "archive_file" "aws_gdpr_guard_layer_zip" {
    depends_on  = [null_resource.prepare_layer]
    type        = "zip"
    source_dir  = "${path.module}/layer/"
    output_path = "${path.module}/aws_gdpr_guard_layer.zip"
}

# Create the Lambda layer
resource "aws_lambda_layer_version" "aws_gdpr_guard_layer" {
    depends_on       = [data.archive_file.aws_gdpr_guard_layer_zip]
    layer_name          = "aws-gdpr-guard-layer"
    description         = "aws_gdpr_guard_layer library layer"
    filename            = data.archive_file.aws_gdpr_guard_layer_zip.output_path
    compatible_runtimes = ["python3.12"]
    source_code_hash    = data.archive_file.aws_gdpr_guard_layer_zip.output_base64sha256
}

# Zip the Lambda code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"
}

# Lambda function
resource "aws_lambda_function" "lambda_function" {
    function_name = "aws-gdpr-guard-lambda"
    runtime = "python3.12"
    timeout = 60
    handler = "lambda_function.lambda_handler"
    role = aws_iam_role.lambda_iam_role.arn
    filename = data.archive_file.lambda_zip.output_path
    layers = [
        "arn:aws:lambda:${var.aws_region}:336392948345:layer:AWSSDKPandas-Python312:2",
        aws_lambda_layer_version.aws_gdpr_guard_layer.arn
    ]

    environment {
      variables = {
        S3_BUCKET_NAME = local.bucket_name
      }
    }
    source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}