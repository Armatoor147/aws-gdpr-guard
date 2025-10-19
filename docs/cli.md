# AWS GDPR Guard - CLI Deployment

## Prerequisites

* AWS account with console access (specifically IAM and S3).
* Python 3.11+ and `pip` installed.


## Deployment Steps

### 1. Create an IAM User and Policy

* Locate the S3 bucket with the file you want to obfuscate.
* Go to **IAM** → **Policies** → **Create policy**:
    - Policy editor: JSON
    - Attach the following custom policy (replace YOUR_BUCKET_NAME with your bucket name):
        ```sh
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
    - Policy name: (e.g., aws-gdpr-guard-s3-access-policy)
* Go to **IAM** → **Users** → **Create user**:
    - User name: (e.g. aws-gdpr-guard-user)
    - Provide user access to the AWS Management Console - optional: No
    - Permissions options: Attach the policy you created
    - Create user
* Generate an access key by entering the IAM user:
    - Go to **Security credentials**
    - Click **Create access key**
    - Use case: Application running outside AWS
    - Store the credentials (Acess key ID and Secret access key) in any of the following ways (boto3 automatically detects them):
        - Using a `.env` file in your root project directory:
            ```
            # .env (environment variables)
            AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
            AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            AWS_REGION=eu-north-1 # Optional
            ```
        - Setting environment variables directly:
            ```sh
            export AWS_ACCESS_KEY_ID="AKIAxxxxxxxxxxxxxxx"
            export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
            ```
        - Using the AWS CLI:
            ```sh
            aws configure
            ```


### 2. Install and Configure the Library

#### Option A: Use GitHub repo

```sh
# Clone the library's GitHub repository:
git clone https://github.com/Armatoor147/aws-gdpr-guard

# Enter the repository
cd aws-gdpr-guard

# Install the dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


#### Option B: Use `pip install`

```sh
# Install the aws_gdpr_guard package
python -m venv venv
source venv/bin/activate
pip install git+https://github.com/Armatoor147/aws-gdpr-guard
```


### 3. Use the Library

* If you cloned the GitHub repository, register the CLI command and install dependencies:
```sh
pip install -e .
```

* To view the obfuscated data from an S3 URI, run:
```sh
aws-gdpr-guard <S3_URI> --pii-fields <PII_FIELDS> --data-type <DATA_TYPE>

# Example
aws-gdpr-guard s3://YOUR_BUCKET_NAME/file_to_obfuscate.csv --pii-fields "name" "email_address" --data-type "csv"
```

* To obfucate the data from one S3 URI and upload it to another, run:
```sh
aws-gdpr-guard <INPUT_S3_URI> --output <OUTPUT_S3_URI> --pii-fields <PII_FIELDS> --data-type <DATA_TYPE>

# Example
aws-gdpr-guard s3://INPUT_BUCKET_NAME/file_to_obfuscate.json --output s3://OUTPUT_BUCKET_NAME/obfuscated_file.json --pii-fields "name" "email_address" --data-type "json"
```


## Notes

- Security Warnings:
    - Never hardcode credentials in your script.
    - Restrict S3 permissions to the specific bucket.
    - If using Git, always add `.env` to your `.gitignore` file.
    - For production, avoid `.env` files (use AWS Secrets Manager or SSM Parameter Store).

- Make sure that the IAM user has S3 GetObject, ListObject (and PutObject if you upload the obfuscated data to S3).
- Make sure that the `data_type` argument matches the data type and the file extension name of the S3 object in `file_to_obfuscate`.
- Supported file types: csv, json, and parquet. Defaults to csv if not specified.