from aws_gdpr_guard.obfuscator import obfuscate_file


# Set LOAD_ENVIRONMENT to True if the AWS credentials are strored in a .env file
# Set LOAD_ENVIRONMENT to False if AWS credentials are exported or configured with `aws configure`
LOAD_ENVIRONMENT = False

if LOAD_ENVIRONMENT:
    import os
    from dotenv import load_dotenv

    load_dotenv()
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def main():
    file_to_obfuscate = "s3://YOUR_BUCKET_NAME/file_to_obfuscate.csv"
    pii_fields = ["name", "email_address"]
    data_type = "csv"
    bytes_data = obfuscate_file(file_to_obfuscate, pii_fields, data_type)
    print(bytes_data)


if __name__ == "__main__":
    main()
