# AWS GDPR Guard - Deployment on ECS

## Prerequisites
* AWS account with console access
* AWS CLI installed and configured
* Terraform installed
* Docker installed


## Deployment Steps

### 1. Create an IAM User and Policy

1. Log in to your AWS Console.
2. Navigate to IAM → Users.
3. Create a new IAM user:
    * User name: e.g. ecs-deployment-iam-user
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
                        "arn:aws:iam::*:role/aws-gdpr-guard-ecs-role",
                        "arn:aws:iam::*:policy/aws-gdpr-guard-ecs-s3-policy",
                        "arn:aws:iam::*:role/aws-gdpr-guard-ecs-task-role",
                        "arn:aws:iam::*:role/aws-gdpr-guard-ecs-task-execution-role"
                    ]
                },
                {
                    "Sid": "S3FullAccess",
                    "Effect": "Allow",
                    "Action": "s3:*",
                    "Resource": [
                        "arn:aws:s3:::aws-gdpr-guard-ecs-deployment-s3-bucket-*",
                        "arn:aws:s3:::aws-gdpr-guard-ecs-deployment-s3-bucket-*/*"
                    ]
                },
                {
                    "Sid": "ECSFullAccess",
                    "Effect": "Allow",
                    "Action": "ecs:*",
                    "Resource": "*"
                },
                {
                    "Sid": "EC2FullAccess",
                    "Effect": "Allow",
                    "Action": "ec2:*",
                    "Resource": "*"
                },
                {
                    "Sid": "CloudWatchLogsFullAccess",
                    "Effect": "Allow",
                    "Action": "logs:*",
                    "Resource": "*"
                },
                {
                    "Sid": "ECRFullAccess",
                    "Effect": "Allow",
                    "Action": "ecr:*",
                    "Resource": "*"
                }
            ]
        }
        ```
4. Generate an access key for the user:
    * Go to Security credentials → Create access key.
    * Select Application running outside AWS.
    * Securely store the Access Key ID and Secret Access Key.


### 2. Set up Docker, Configure AWS CLI and Deploy with Terraform

- Write a Dockerfile and a .dockerignore file (A functioning example is already written in the root directory)
- Run the following:
```sh
# Build Docker image
docker build --platform linux/amd64 -t aws-gdpr-guard .

# Run Docker container locally (and check that the Python script can run before implementing AWS)
docker run -it --rm aws-gdpr-guard

# Create ECR repository
aws ecr create-repository --repository-name aws-gdpr-guard

# Tag Docker image
docker tag aws-gdpr-guard:latest <account-id>.dkr.ecr.<region>.amazonaws.com/aws-gdpr-guard:latest

# Log in to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

# Push Docker image
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/aws-gdpr-guard:latest
```

- Apply Terraform:
```sh
# Configure AWS CLI with the IAM user credentials
aws configure

# Navigate to the Terraform directory for ECS deployment
cd terraform-ecs-deployment

# Apply Terraform
terraform apply
# Enter your ECR repository URI (<account-id>.dkr.ecr.<region>.amazonaws.com/aws-gdpr-guard)
```


### 3. Test the ECS Cluster

- Go to **Amazon Elastic Container Service** → **Clusters**, and enter your ECS cluster (e.g. aws-gdpr-guard-cluster).
    - Click **Tasks** → **Run new Task**.
    - Select "Task definition family"  (e.g. aws-gdpr-guard-task).
    - Launch type: FARGATE.
    - Select security group with outbound access only (e.g. aws-gdpr-guard-ecs-service-sg).
    - Click **Create**.
- Enter the created task and go to **Logs**.
    - You will see the output of the Python script displayed.


### 4. Cleanup

Once finished with the Docker image, the ECR repository and the ECS resources, you can delete them to free up space.
```sh
# List all Docker images
docker images

# Delete the specific image
docker rmi aws-gdpr-guard:latest
docker rmi <account-id>.dkr.ecr.<region>.amazonaws.com/aws-gdpr-guard:latest



# List images in your ECR repository
aws ecr list-images --repository-name aws-gdpr-guard

# Delete the image (replace <image-digest> with the actual digest from the list-images command)
aws ecr batch-delete-image --repository-name aws-gdpr-guard --image-ids imageDigest=<image-digest>

# Delete the ECR repository
aws ecr delete-repository --repository-name aws-gdpr-guard --force

# Delete all resources created by Terraform
terraform destroy
```

## Notes

* Ensure the Docker image is built for the correct platform (`linux/amd64`).
* Make sure the IAM user's AWS region matches with the Terraform configuration.