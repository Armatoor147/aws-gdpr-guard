import os
from dotenv import load_dotenv
import pandas as pd
import boto3
import re

# Get AWS credentials
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

def split_S3_URI(s3_uri):
    pattern = r'^s3://([^/]+)/(.*)$'
    match = re.search(pattern, s3_uri)
    bucket_name = match.group(1)
    object_name = match.group(2)
    return bucket_name, object_name

def read_CSV_file_from_S3_bucket(s3_client, bucket_name, object_name):
    object = s3_client.get_object(
        Bucket=bucket_name,
        Key=object_name
    )
    data = pd.read_csv(object["Body"])
    return data

def obfuscate_df(data, pii_fields):
    columns = data.columns
    for column in columns:
        if column in pii_fields:
            data[column] = "***"
    return data


def obfuscate_file(file_to_obfuscate, pii_fields):
    """
    Obfuscates file from an S3 bucket.

    Args:
        file_to_obfuscate: S3 URI of the S3 bucket file.
        pii_fields: List of column names to obfuscate.

    Returns:
        Obfuscated CSV as bytes.

    Raises:
        [Complete this once I know what needs to be raised]
    """

    # Extract bucket name and object name from the S3 URI
    bucket_name, object_name = split_S3_URI(file_to_obfuscate)
    
    # Connect to S3 client
    s3_client = boto3.client("s3")
    
    # Save S3 bucket (CSV) file as a table variable
    data = read_CSV_file_from_S3_bucket(s3_client, bucket_name, object_name)

    # Obfuscate relevant columns
    data = obfuscate_df(data, pii_fields)
    
    # Return Obfuscated table
    return data
    



if __name__ == "__main__":
    file_to_obfuscate = "s3://vincent-toor-azorin-aws-gdpr-guard-test-bucket/dummy_students.csv"
    pii_fields = ["name", "email_address"]
    data = obfuscate_file(file_to_obfuscate, pii_fields)
    print(data)
    


    
    
