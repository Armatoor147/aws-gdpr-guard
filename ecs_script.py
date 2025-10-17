from aws_gdpr_guard.obfuscator import obfuscate_file
# import boto3


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
    file_to_obfuscate = (
        "s3://vincent-toor-azorin-aws-gdpr-guard-test-bucket/dummy_students.csv"
    )
    pii_fields = ["name", "email_address"]
    data_type = "csv"
    bytes_data = obfuscate_file(file_to_obfuscate, pii_fields, data_type)
    print(bytes_data)

    # s3_client = boto3.client("s3")
    # s3_client.put_object(
    #     Bucket="vincent-toor-azorin-aws-gdpr-guard-test-bucket",
    #     Key="obfuscated_dummy_students.csv",
    #     Body=bytes_data
    # )


    # import pandas as pd
    # import io
    # file_path = "s3://vincent-toor-azorin-aws-gdpr-guard-test-bucket/obfuscated_dummy_students.parquet"
    # bucket_name = "vincent-toor-azorin-aws-gdpr-guard-test-bucket"
    # object_key = "obfuscated_dummy_students.parquet"
    # s3_client = boto3.client("s3")
    # response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    # data = pd.read_parquet(io.BytesIO(response['Body'].read()))
    
    # df = pd.read_parquet(file_path)
    # print(data)


if __name__ == "__main__":
    main()
