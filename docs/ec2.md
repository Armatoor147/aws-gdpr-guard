# AWS GDPR Guard - Deployment on EC2

## Prerequisites
* AWS account with console access
* AWS CLI installed and configured
* Terraform installed


## Deployment Steps

### 1. Create an IAM User and Policy

1. Log in to your AWS Console.
2. Navigate to IAM → Users.
3. Create a new IAM user:
    * User name: e.g. ec2-deployment-iam-user
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
                        "arn:aws:iam::*:role/aws-gdpr-guard-ec2-role",
                        "arn:aws:iam::*:policy/aws-gdpr-guard-ec2-s3-policy"
                    ]
                },
                {
                    "Sid": "S3FullAccess",
                    "Effect": "Allow",
                    "Action": "s3:*",
                    "Resource": [
                        "arn:aws:s3:::aws-gdpr-guard-ec2-deployment-s3-bucket-*",
                        "arn:aws:s3:::aws-gdpr-guard-ec2-deployment-s3-bucket-*/*"
                    ]
                },
                {
                    "Sid": "EC2FullAccess",
                    "Effect": "Allow",
                    "Action": "ec2:*",
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

# Navigate to the Terraform directory for EC2 deployment
cd terraform-ec2-deployment

# Run pre-terraform configuration and apply terraform
chmod +x pre_terraform.sh
./pre_terraform.sh
terraform apply
```


### 3. Test the EC2 Instance

After applying Terraform, the public IP of the EC2 instance will be output in your terminal. Use this IP to connect to the instance via SSH:
```sh
# Ensure the SSH key has the correct permissions
chmod 400 keys/aws_gdpr_guard_key.pem

# Connect to the EC2 instance
ssh -i keys/aws_gdpr_guard_key.pem ec2-user@<EC2_instance_IP>
```

Once inside the EC2 instance, running the following commands:
```sh
# Set up the environment
chmod +x ec2_setup.sh
./ec2_setup.sh

# Activate the virtual environment
source venv/bin/activate

# Run the script to see the obfuscated data
python3 ec2_script.py
```


### 4. Cleanup

```sh
# Delete all resources created by Terraform
terraform destroy

# Clean up pre-Terraform and Terraform-generated files
rm terraform.tfvars
rm -r keys/
rm aws_gdpr_guard.zip
```


## Notes

* Always keep your .pem key secure and never share it.
* If SSH fails, ensure the security group allows inbound traffic on port 22 and that the key is correct.
* Make sure the IAM user's AWS region matches with the Terraform configuration.