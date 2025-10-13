import os
import io
import pandas as pd
import boto3
from botocore.exceptions import ClientError
import re
from typing import Tuple, Sequence


# Get AWS credentials
IS_LOCAL = os.getenv("AWS_LAMBDA_FUNCTION_NAME") is None
if IS_LOCAL:
    from dotenv import load_dotenv

    load_dotenv()
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def split_s3_uri(s3_uri: str) -> Tuple[str, str]:
    """
    Splits an S3 URI (e.g., 's3://bucket-name/key/file.csv') into the bucket name and object key.

    Args:
        s3_uri: S3 URI of the S3 bucket file.

    Returns:
        bucket_name: Name of the S3 bucket.
        object_name: Key of the CSV file in the bucket.

    Raises:
        ValueError: If the URI does not match the expected S3 pattern.
    """
    pattern = r"^s3://([^/]+)/(.*)$"
    match = re.search(pattern, s3_uri)
    if match:
        bucket_name = match.group(1)
        object_name = match.group(2)
        return bucket_name, object_name
    else:
        raise ValueError(f"Invalid S3 URI format")


def read_file_from_s3_bucket(
    s3_client, bucket_name: str, object_name: str, file_type: str = "csv"
) -> pd.DataFrame:
    """
    Reads a CSV file from an S3 bucket and returns a pandas DataFrame.

    Args:
        s3_client: A boto3 S3 client instance.
        bucket_name: Name of the S3 bucket.
        object_name: Key of the file in the bucket.
        file_type: Type of the file ("csv", "json", or "parquet"). Defaults to "csv".

    Returns:
        pd.DataFrame: Parsed file data as a DataFrame.

    Raises:
        ValueError: If the file_type is not supported.
        ClientError: If the S3 object cannot be fetched or parsed.
        pd.errors.EmptyDataError: If the dataframe is empty.
        Exception: For other unexpected errors.
    """
    try:
        object = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        if file_type == "csv":
            data = pd.read_csv(object["Body"])
        elif file_type == "json":
            data = pd.read_json(object["Body"])
        elif file_type == "parquet":
            data = pd.read_parquet(io.BytesIO(object["Body"].read()))
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        return data
    except ClientError:
        raise ClientError(
            error_response={"Error": {"Code": "404", "Message": "S3 access issue"}},
            operation_name="GetObject",
        )
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError(f"{file_type.upper()} file is empty")
    except ValueError:
        raise
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

    if not isinstance(pii_fields, list) or not all(
        isinstance(field, str) for field in pii_fields
    ):
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


def dataframe_to_bytes(data: pd.DataFrame, file_type: str = "csv") -> bytes:
    """
    Converts a pandas DataFrame to bytes in CSV, JSON, or Parquet format.

    Args:
        data: The DataFrame to convert.
        file_type: The output format ("csv", "json", or "parquet"). Defaults to "csv".

    Returns:
        bytes: The DataFrame as bytes in the specified format.

    Raises:
        ValueError: If the file_type is not supported.
        Exception: For other unexpected errors.
    """
    try:
        if file_type == "csv":
            bytes_data = data.to_csv(index=False).encode()
        elif file_type == "json":
            bytes_data = data.to_json(orient="records", index=False).encode()
        elif file_type == "parquet":
            buffer = io.BytesIO()
            data.to_parquet(buffer, engine="pyarrow", index=False)
            bytes_data = buffer.getvalue()
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        return bytes_data
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


def obfuscate_file(
    file_to_obfuscate: str,
    pii_fields: Sequence[str],
    data_type: str = "csv",
) -> bytes:
    """
    Obfuscates file from an S3 bucket.

    Args:
        file_to_obfuscate: S3 URI of the S3 bucket file.
        pii_fields: List of column names to obfuscate.
        data_type: The output bytes' data type ("csv", "json", or "parquet"). Defaults to "csv".

    Returns:
        Obfuscated data as bytes.

    Raises:
        ObfuscationError:
            ValueError: If the file_type is not supported, if `pii_fields` contains a column not present in `data`.
            ClientError: If the S3 object cannot be fetched or parsed.
            pd.errors.EmptyDataError: If the dataframe is empty.
            TypeError: If `pii_fields` is not a list of strings or `data` is not a DataFrame.
            Exception: For other unexpected errors.
    """

    try:
        # Extract the bucket name and object name from the S3 URI
        bucket_name, object_name = split_s3_uri(file_to_obfuscate)

        # Connect to the S3 client
        s3_client = boto3.client("s3")

        # Save the S3 bucket file as a dataframe
        data_df = read_file_from_s3_bucket(
            s3_client, bucket_name, object_name, data_type
        )

        # Obfuscate relevant columns
        obfuscated_data_df = obfuscate_df(data_df, pii_fields)

        # Turn the dataframe into bytes
        bytes_data = dataframe_to_bytes(obfuscated_data_df, data_type)

        # Return obfuscated data
        return bytes_data

    except ClientError as e:
        raise ObfuscationError(f"S3 access failed: {e}") from e
    except pd.errors.EmptyDataError as e:
        raise ObfuscationError(f"Input file is empty: {e}") from e
    except ValueError as e:
        raise ObfuscationError(f"Invalid configuration or data: {e}") from e
    except TypeError as e:
        raise ObfuscationError(f"Invalid data types or parameters: {e}") from e
    except Exception as e:
        raise ObfuscationError(f"Unexpected obfuscation error: {e}") from e


class ObfuscationError(Exception):
    """Raised when the obfuscation process fails."""

    pass


if __name__ == "__main__":
    file_to_obfuscate = (
        "s3://vincent-toor-azorin-aws-gdpr-guard-test-bucket/dummy_students.parquet"
    )
    pii_fields = ["name", "email_address"]
    data_type = "parquet"
    bytes_data = obfuscate_file(file_to_obfuscate, pii_fields, data_type)
    print(bytes_data)

    # buffer = io.BytesIO(bytes_data)
    # df = pd.read_parquet(buffer)
    # print(df)

    # s3_client = boto3.client("s3")
    # s3_client.put_object(Bucket="vincent-toor-azorin-aws-gdpr-guard-test-bucket", Key="obfuscated_dummy_students.csv", Body=bytes_data)

    # file_to_read = "s3://vincent-toor-azorin-aws-gdpr-guard-test-bucket/obfuscated_dummy_students.csv"
    # bucket_name, object_name = split_s3_uri(file_to_read)
    # s3_client = boto3.client("s3")
    # data = read_file_from_s3_bucket(s3_client, bucket_name, object_name)
    # print(data)
