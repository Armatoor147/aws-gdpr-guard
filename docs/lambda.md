# AWS GDPR Guard - Deployment on AWS Lambda

## Prerequisites
* AWS account with console access
* AWS CLI installed and configured
* Terraform installed


## Deployment Steps

### 1. Create an IAM User and Policy

1. Log in to your AWS Console.
2. Navigate to IAM → Users.
3. Create a new IAM user:
    * User name: e.g. lambda-deployment-iam-user
    * Attach the following inline policy:
        ```sh
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "IAMFullAccess",
                    "Effect": "Allow",
                    "Action": "iam:*",
                    "Resource": [
                        "arn:aws:iam::*:role/aws-gdpr-guard-lambda-role",
                        "arn:aws:iam::*:policy/aws-gdpr-guard-lambda-s3-policy"
                    ]
                },
                {
                    "Sid": "S3FullAccess",
                    "Effect": "Allow",
                    "Action": "s3:*",
                    "Resource": [
                        "arn:aws:s3:::aws-gdpr-guard-s3-bucket-*",
                        "arn:aws:s3:::aws-gdpr-guard-s3-bucket-*/*"
                    ]
                },
                {
                    "Sid": "LambdaFullAccess",
                    "Effect": "Allow",
                    "Action": "lambda:*",
                    "Resource": "*"
                }
            ]
        }
        ```
4. Generate an access key for the user:
    * Go to Security credentials → Create access key.
    * Select Application running outside AWS.
    * Securely store the Access Key ID and Secret Access Key.

### 2. Configure AWS CLI and Deploy with Terraform

Run the following commands in your terminal:
```sh
# Configure AWS CLI with the IAM user credentials
aws configure

# Navigate to the Terraform directory for Lambda deployment
cd terraform-lambda-deployment/

# Initialize Terraform
terraform init

# Apply Terraform configuration
terraform apply
```

### 3. Test the Lambda Function
After applying Terraform, the name of the Lambda function will be output in your terminal.

1. Go to the AWS Console → Lambda.
2. Locate and select the deployed Lambda function using the output name.
3. You can:
    * Run the function as-is to see the obfuscated data printed in the logs.
    * Modify the code with your own script if needed, then test again.


## Notes

* Replace placeholder values (e.g., bucket names, roles, instances) as needed.
* Add or change the IAM user/policy to your convenience if more permissions are required.
* Store credentials securely (e.g., AWS Secrets Manager, encrypted local files).
* Review the Terraform plan before applying.