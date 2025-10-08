# GDPR Obfuscator Project
## Project Summary

ADD EXPLANATION!!!


## Implementation
### Option A: Local Testing
#### 1. Prerequisites

Before using the library, ensure you have:
* An AWS account with access to IAM and S3.
* Python 3.8+ and `pip` installed.
* The library installed:
```sh
pip install aws_gdpr_guard
```


#### 2. AWS Setup

* Locate the S3 bucket with the file that you want to obfuscate.
* Go to **IAM** → **Policies** → **Create policy**:
    - Policy editor: JSON
    - Attach the following custom policy:
        ```
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowGetObject",
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
                },
                {
                    "Sid": "AllowListBucket",
                    "Effect": "Allow",
                    "Action": "s3:ListBucket",
                    "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME"
                },
                {
                    "Sid": "AllowPutObject",
                    "Effect": "Allow",
                    "Action": "s3:PutObject",
                    "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
                }
            ]
        }
        ```
    - Policy name: (e.g. S3-Access-aws_gdpr_guard_user)
* Go to **IAM** → **Users** → **Create user**:
    - User name: (e.g. aws_gdpr_guard_user)
    - Provide user access to the AWS Management Console - optional: No
    - Permissions options: Attach policies directly
    - Permissions policies: [Find the IAM policy that you created] (e.g. S3-Access-aws_gdpr_guard_user)
* Go to **IAM** → **Users**
* Enter the IAM user that you created:
    - Go to **Security credentials**
    - Click **Create access key**
    - Use case: Application running outside AWS
    - Copy and paste the credentials (Acess key ID and Secret access key) into a `.env` file in your root project directory:
        ```
        #.env (environment variables)
        AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
        AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        AWS_REGION=eu-north-1 # Optional
        ```


#### 3. Install and Configure the Library
* Install Dependencies:
    ```sh
    pip install requirements.txt
    ```
* Create a Python file
* Load Credentials:
    ```python
    from dotenv import load_dotenv
    load_dotenv()  # Loads AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    ```
* Use the Library:
    ```python
    from aws_gdpr_guard import obfuscate_file
    obfuscated_data = obfuscate_file(
        file_to_obfuscate="s3://YOUR_BUCKET_NAME/path/to/file.csv"
        pii_fields=["name", "email", "phone_number"] # Columns to obfuscate
    )
    ```

* Example Workflow:
    ```python
    from dotenv import load_dotenv
    from aws_gdpr_guard import obfuscate_file
    import boto3

    load_dotenv()
    obfuscated_data = obfuscate_file(
        file_to_obfuscate="s3://YOUR_BUCKET_NAME/file_to_obfuscate.csv"
        pii_fields=["name", "email", "phone_number"]
    )
    s3_client = boto3.client("s3")

    # Store obfuscated data into an S3 bucket file (IAM user must have PutObject permission on the S3 bucket)
    s3_client.put_object(
        Bucket="YOUR_BUCKET_NAME",
        Key="obfuscated_file.csv",
        Body=obfuscated_data
    )
    ```

* Security Warnings:
    - Never hardcode credentials in your script.
    - Restrict S3 permissions to the specific bucket.
    - For production, use IAM roles (not IAM users) and avoid .env files (use AWS Secrets Manager or SSM Parameter Store).


### Option B (AWS Lambda)

- create IAM user:
    ...
* Go to **IAM** → **Users**
* Enter the IAM user that you created:
    - Go to **Security credentials**
    - Click **Create access key**
    - Use case: Application running outside AWS
    - Copy and paste the credentials (Acess key ID and Secret access key) safely (e.g. AWS Secrets Manager?)
* Go to your local terminal and enter:
    ```bash
    aws configure
    ```
* Enter credentials 

### Option C (EC2)
Manually:
- Launch EC2 instance
- Connect to instance
    In terminal:
        ```bash
        chmod 400 aws_gdpr_guard_key.pem
        ssh -i "keys/aws_gdpr_guard_key.pem" ec2-user@51.21.255.135
        exit
        ```
- Transfer Python library
    In terminal:
        ```bash
        scp -i keys/aws_gdpr_guard_key.pem -r aws_gdpr_guard/ ec2-user@51.21.255.135:/home/ec2-user/
        ```
- Install dependencies
    In EC2 instance:
        ```bash
        sudo yum update
        sudo yum install python3 python3-pip
        pip3 install -r aws_gdpr_guard/requirements.txt
        ```
- Run library
    In EC2 instance:
        ```bash
        python3 ec2_script.py
        ```

Terraform:
```bash
cd terraform-ec2-deployment
chmod +x pre_terraform.sh
./pre_terraform.sh
terraform apply
```

Copy the EC2 instance's public IP from the terraform ouput and enter EC2 instance:
```bash
chmod 400 keys/aws_gdpr_guard_key.pem # If the SSH connection below doesn't work
ssh -i keys/aws_gdpr_guard_key.pem ec2-user@<EC2_instance_IP>
```

Setup:
```bash
chmod +x ec2_setup.sh
./ec2_setup.sh
```

Source into virtual environment:
```bash
source venv/bin/activate
```

Run script:
```bash
python3 ec2_script.py
```


## Troubleshooting
* `"AccessDenied"` errors? Check IAM policies and bucket names.
* Missing `.env`? Ensure the file is in the same directory as your script.


## FAQ
* *"Can I obfuscate multiple files?"* → Yes, loop over a list of `s3_uri`s.
* *"How do I verify the obfuscation?"* → Download the file from S3 and inspect it.

