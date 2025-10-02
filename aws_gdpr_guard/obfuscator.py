import os
from dotenv import load_dotenv
import pandas as pd
import boto3
from botocore.exceptions import ClientError
import re
from typing import Tuple, Sequence


# Get AWS credentials
IS_LOCAL = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is None
if IS_LOCAL:
    from dotenv import load_dotenv
    load_dotenv()
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

def split_S3_URI(s3_uri: str) -> Tuple[str, str]:
    """
    Splits an S3 URI (e.g., 's3://bucket-name/key/file.csv') into the bucket name and object key.

    Args:
        s3_uri: S3 URI of the S3 bucket file.

    Returns:
        bucket_name:
        object_name:
    
    Raises:
        A ValueError if the URI does not match the expected S3 pattern.
    """
    pattern = r"^s3://([^/]+)/(.*)$"
    match = re.search(pattern, s3_uri)
    if match:
        bucket_name = match.group(1)
        object_name = match.group(2)
        return bucket_name, object_name
    else:
        raise ValueError(f"Invalid S3 URI format")


def read_CSV_file_from_S3_bucket(s3_client, bucket_name: str, object_name: str) -> pd.DataFrame:
    """
    Reads a CSV file from an S3 bucket and returns a pandas DataFrame.

    Args:
        s3_client: A boto3 S3 client instance.
        bucket_name: Name of the S3 bucket.
        object_name: Key of the CSV file in the bucket.

    Returns:
        pd.DataFrame: Parsed CSV data as a DataFrame.

    Raises:
        Exception: If the S3 object cannot be fetched or parsed.
    """
    try:
        object = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        data = pd.read_csv(object["Body"])
        return data
    except ClientError:
        raise ClientError(
            error_response={"Error": {"Code": "404", "Message": "S3 access issue"}},
            operation_name="GetObject"
        )
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError("CSV file is empty")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


def obfuscate_df(data: pd.DataFrame, pii_fields: Sequence[str]) -> pd.DataFrame:
    """
    Obfuscates sensitive columns in a DataFrame by replacing their values with '***'.

    Args:
        data: Input DataFrame containing potential PII (Personally Identifiable Information).
        pii_fields: List of column names to obfuscate.

    Returns:
        pd.DataFrame: A new DataFrame with specified PII columns obfuscated.
                      Non-PII columns remain unchanged.

    Raises:
        TypeError: If `pii_fields` is not a list of strings or `data` is not a DataFrame.
        ValueError: If `pii_fields` contains a column not present in `data`.
    """

    # Input validation
    if not isinstance(data, pd.DataFrame):
        raise TypeError("`data` must be a pandas DataFrame.")

    if not isinstance(pii_fields, list) or not all(isinstance(field, str) for field in pii_fields):
        raise TypeError("`pii_fields` must be a list of strings.")

    # Check for non-existent columns
    missing_columns = set(pii_fields) - set(data.columns)
    if missing_columns:
        raise ValueError(
            f"Columns not found in DataFrame: {missing_columns}. "
            f"Available columns: {list(data.columns)}"
        )
    
    # Obfuscate PII fields
    data = data.copy()
    for column in pii_fields:
        data[column] = "***"
    
    return data


def obfuscate_file(file_to_obfuscate: str, pii_fields: Sequence[str]):
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

    try:
        # Extract bucket name and object name from the S3 URI
        bucket_name, object_name = split_S3_URI(file_to_obfuscate)

        # Connect to S3 client
        s3_client = boto3.client("s3")

        # Save S3 bucket (CSV) file as a table variable
        data_df = read_CSV_file_from_S3_bucket(s3_client, bucket_name, object_name)

        # Obfuscate relevant columns
        obfuscated_data_df = obfuscate_df(data_df, pii_fields)

        # Turn dataframe to bytes
        bytes_data = obfuscated_data_df.to_csv(index=False).encode()

        # Return Obfuscated table
        return bytes_data
    except:
        # Handle every type of error in obfuscate_file !!!
        pass



if __name__ == "__main__":
    # file_to_obfuscate = (
    #     "s3://vincent-toor-azorin-aws-gdpr-guard-test-bucket/dummy_students.csv"
    # )
    # pii_fields = ["name", "email_address"]
    # data = obfuscate_file(file_to_obfuscate, pii_fields)
    # bytes_data = data.to_csv(index=False).encode()

    # s3_client = boto3.client("s3")
    # s3_client.put_object(Bucket="vincent-toor-azorin-aws-gdpr-guard-test-bucket", Key="obfuscated_dummy_students.csv", Body=bytes_data)

    file_to_read = "s3://vincent-toor-azorin-aws-gdpr-guard-test-bucket/obfuscated_dummy_students.csv"
    bucket_name, object_name = split_S3_URI(file_to_read)
    s3_client = boto3.client("s3")
    data = read_CSV_file_from_S3_bucket(s3_client, bucket_name, object_name)
    print(data)
    

    
