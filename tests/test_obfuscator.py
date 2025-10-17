from aws_gdpr_guard.obfuscator import (
    split_s3_uri,
    read_file_from_s3_bucket,
    obfuscate_df,
    dataframe_to_bytes,
    obfuscate_file,
    ObfuscationError,
)
import aws_gdpr_guard.obfuscator
import pytest
from unittest.mock import MagicMock, Mock, patch
from moto import mock_aws
from io import StringIO, BytesIO
import io
import pandas as pd
import boto3
import json
from botocore.exceptions import ClientError


class Test_split_s3_uri:
    def test_split_s3_uri_sucessful(self):
        s3_uri = "s3://test-bucket/test-file.csv"
        expected_bucket_name = "test-bucket"
        expected_object_name = "test-file.csv"
        bucket_name, object_name = split_s3_uri(s3_uri)
        assert bucket_name == expected_bucket_name
        assert object_name == expected_object_name

    def test_split_s3_uri_ValueError(self):
        s3_uri = "s2://test-bucket/test-file.csv"
        with pytest.raises(ValueError, match="Invalid S3 URI format"):
            split_s3_uri(s3_uri)


@mock_aws
class Test_read_file_from_s3_bucket:
    def test_read_file_from_s3_bucket_csv_successful(self):
        test_csv_data = "name,sport\nRonaldo,Football\nHamilton,F1\nNadal,Tennis"
        test_bucket = "test-bucket"
        test_object = "test-file.csv"

        # mock_streaming_body = StringIO(test_csv_data)
        # mock_s3_client = MagicMock()
        # mock_s3_client.get_object.return_value = {"Body": mock_streaming_body}

        mock_s3_client = boto3.client("s3", region_name="us-east-1")
        mock_s3_client.create_bucket(Bucket=test_bucket)
        mock_s3_client.put_object(
            Bucket=test_bucket, Key=test_object, Body=test_csv_data
        )

        expected = pd.DataFrame(
            {
                "name": ["Ronaldo", "Hamilton", "Nadal"],
                "sport": ["Football", "F1", "Tennis"],
            }
        )
        result = read_file_from_s3_bucket(mock_s3_client, test_bucket, test_object)

        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, expected)
        # mock_s3_client.get_object.assert_called_once_with(Bucket=test_bucket, Key=test_object)

    def test_read_file_from_s3_bucket_json_successful(self):
        test_json_data = [
            {"name": "Ronaldo", "sport": "Football"},
            {"name": "Hamilton", "sport": "F1"},
            {"name": "Nadal", "sport": "Tennis"},
        ]
        test_bucket = "test-bucket"
        test_object = "test-file.json"
        file_type = "json"
        mock_s3_client = boto3.client("s3", region_name="us-east-1")
        mock_s3_client.create_bucket(Bucket=test_bucket)
        mock_s3_client.put_object(
            Bucket=test_bucket, Key=test_object, Body=json.dumps(test_json_data)
        )

        expected = pd.DataFrame(
            pd.DataFrame(
                {
                    "name": ["Ronaldo", "Hamilton", "Nadal"],
                    "sport": ["Football", "F1", "Tennis"],
                }
            )
        )
        result = read_file_from_s3_bucket(
            mock_s3_client, test_bucket, test_object, file_type
        )

        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, expected)

    def test_read_file_from_s3_bucket_parquet_successful(self):
        df = pd.DataFrame(
            {
                "name": ["Ronaldo", "Hamilton", "Nadal"],
                "sport": ["Football", "F1", "Tennis"],
            }
        )
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        test_parquet_data = parquet_buffer.getvalue()
        test_bucket = "test-bucket"
        test_object = "test-file.parquet"
        file_type = "parquet"

        mock_s3_client = boto3.client("s3", region_name="us-east-1")
        mock_s3_client.create_bucket(Bucket=test_bucket)
        mock_s3_client.put_object(
            Bucket=test_bucket, Key=test_object, Body=test_parquet_data
        )

        expected = pd.DataFrame(
            pd.DataFrame(
                {
                    "name": ["Ronaldo", "Hamilton", "Nadal"],
                    "sport": ["Football", "F1", "Tennis"],
                }
            )
        )
        result = read_file_from_s3_bucket(
            mock_s3_client, test_bucket, test_object, file_type
        )

        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, expected)

    def test_read_file_from_s3_bucket_ValueError(self):
        mock_s3_client = MagicMock()
        test_bucket = "test-bucket"
        test_object = "test-file.txt"
        file_type = "txt"
        mock_s3_client.create_bucket(Bucket=test_bucket)
        with pytest.raises(Exception, match="Unsupported file type: txt"):
            read_file_from_s3_bucket(
                mock_s3_client, test_bucket, test_object, file_type
            )

    def test_read_file_from_s3_bucket_ClientError(self):
        mock_s3_client = MagicMock()
        test_bucket = "test-bucket"
        test_object = "test-file.csv"
        mock_s3_client.create_bucket(Bucket=test_bucket)
        mock_s3_client.get_object.side_effect = ClientError(
            error_response={"Error": {"Code": "404", "Message": "S3 access issue"}},
            operation_name="GetObject",
        )
        with pytest.raises(ClientError, match="S3 access issue"):
            read_file_from_s3_bucket(mock_s3_client, test_bucket, test_object)

    def test_read_file_from_s3_bucket_EmptyDataError(self):
        mock_s3_client = MagicMock()
        mock_s3_client.get_object.return_value = {"Body": StringIO("")}
        test_bucket = "test-bucket"
        test_object = "test-file.csv"
        with pytest.raises(pd.errors.EmptyDataError, match="CSV file is empty"):
            read_file_from_s3_bucket(mock_s3_client, test_bucket, test_object)

    def test_read_file_from_s3_bucket_Exception(self):
        mock_s3_client = MagicMock()
        mock_s3_client.get_object.side_effect = RuntimeError
        test_bucket = "test-bucket"
        test_object = "test-file.csv"
        with pytest.raises(Exception):
            read_file_from_s3_bucket(mock_s3_client, test_bucket, test_object)


class Test_obfuscate_df:
    def test_obfuscate_df_successful(self):
        data = pd.DataFrame(
            {
                "name": ["Ronaldo", "Hamilton", "Nadal"],
                "sport": ["Football", "F1", "Tennis"],
            }
        )
        pii_fields = ["sport"]
        expected = pd.DataFrame(
            {"name": ["Ronaldo", "Hamilton", "Nadal"], "sport": ["***", "***", "***"]}
        )
        result = obfuscate_df(data, pii_fields)
        pd.testing.assert_frame_equal(result, expected)

    def test_obfuscate_df_TypeError_data(self):
        data = "Not a pd.DataFrame"
        pii_fields = ["sports"]
        with pytest.raises(TypeError, match="`data` must be a pandas DataFrame."):
            obfuscate_df(data, pii_fields)

    def test_obfuscate_df_TypeError_pii_fields(self):
        data = pd.DataFrame(
            {
                "name": ["Ronaldo", "Hamilton", "Nadal"],
                "sport": ["Football", "F1", "Tennis"],
            }
        )
        pii_fields = ["sports", 1234]
        with pytest.raises(TypeError, match="`pii_fields` must be a list of strings."):
            obfuscate_df(data, pii_fields)

    def test_obfuscate_df_ValueError(self):
        data = pd.DataFrame(
            {
                "name": ["Ronaldo", "Hamilton", "Nadal"],
                "sport": ["Football", "F1", "Tennis"],
            }
        )
        pii_fields = ["age"]
        expected_match = r"Columns not found in DataFrame: \{\'age\'\}. Available columns: \['name', 'sport'\]"
        with pytest.raises(ValueError, match=expected_match):
            obfuscate_df(data, pii_fields)


class Test_dataframe_to_bytes:
    def test_dataframe_to_bytes_csv_successful(self):
        data = pd.DataFrame(
            {
                "name": ["Ronaldo", "Hamilton", "Nadal"],
                "sport": ["Football", "F1", "Tennis"],
            }
        )
        file_type = "csv"
        expected = b"name,sport\nRonaldo,Football\nHamilton,F1\nNadal,Tennis\n"
        result = dataframe_to_bytes(data, file_type)
        assert result == expected

    def test_dataframe_to_bytes_json_successful(self):
        data = pd.DataFrame(
            {
                "name": ["Ronaldo", "Hamilton", "Nadal"],
                "sport": ["Football", "F1", "Tennis"],
            }
        )
        file_type = "json"
        expected = b'[{"name":"Ronaldo","sport":"Football"},{"name":"Hamilton","sport":"F1"},{"name":"Nadal","sport":"Tennis"}]'
        result = dataframe_to_bytes(data, file_type)
        assert result == expected

    def test_dataframe_to_bytes_parquet_successful(self):
        data = pd.DataFrame(
            {
                "name": ["Ronaldo", "Hamilton", "Nadal"],
                "sport": ["Football", "F1", "Tennis"],
            }
        )
        file_type = "parquet"
        expected_df = pd.DataFrame(
            {
                "name": ["Ronaldo", "Hamilton", "Nadal"],
                "sport": ["Football", "F1", "Tennis"],
            }
        )
        result = dataframe_to_bytes(data, file_type)
        result_df = pd.read_parquet(io.BytesIO(result))
        print(result_df)
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_dataframe_to_bytes_ValueError(self):
        data = pd.DataFrame(
            {
                "name": ["Ronaldo", "Hamilton", "Nadal"],
                "sport": ["Football", "F1", "Tennis"],
            }
        )
        file_type = "txt"
        with pytest.raises(ValueError, match="Unsupported file type: txt"):
            dataframe_to_bytes(data, file_type)

    def test_dataframe_to_bytes_Exception(self, monkeypatch):
        # Create a valid dataframe
        df = pd.DataFrame({"a": [1, 2, 3]})

        # Monkeypatch the to_csv method to raise an unexpected exception
        def mock_to_csv(*args, **kwargs):
            raise RuntimeError("Simulated CSV failure")

        monkeypatch.setattr(df, "to_csv", mock_to_csv)

        # This should trigger the generic Exception catch block
        with pytest.raises(Exception, match="Unexpected error: Simulated CSV failure"):
            dataframe_to_bytes(df, file_type="csv")


# @patch("aws_gdpr_guard.obfuscator.boto3.client")
@mock_aws
class Test_obfuscate_file:
    def test_obfuscate_file_successful(self):
        file_to_obfuscate = "s3://test-bucket/test-file.csv"
        pii_fields = ["sport"]

        # mock_s3_client = Mock()
        # test_csv_data = "name,sport\nRonaldo,Football\nHamilton,F1\nNadal,Tennis"
        # mock_s3_response = {"Body": StringIO(test_csv_data)}
        # mock_s3_client.get_object.side_effect = lambda Bucket, Key: (
        #     mock_s3_response if (Bucket, Key) == ("test-bucket", "test-file.csv")
        #     else Exception(f"Unexpected call with Bucket={Bucket}, Key={Key}")
        # )
        # mock_boto3_client.return_value = mock_s3_client

        s3_client = boto3.client("s3", region_name="us-east-1")
        test_bucket = "test-bucket"
        test_key = "test-file.csv"
        s3_client.create_bucket(Bucket=test_bucket)
        csv_data = "name,sport\nRonaldo,Football\nHamilton,F1\nNadal,Tennis"
        s3_client.put_object(Bucket=test_bucket, Key=test_key, Body=csv_data)

        expected = b"name,sport\nRonaldo,***\nHamilton,***\nNadal,***\n"
        result = obfuscate_file(file_to_obfuscate, pii_fields)

        # mock_boto3_client.assert_called_once_with("s3")
        # mock_s3_client.get_object.assert_called_once_with(
        #     Bucket="test-bucket",
        #     Key="test-file.csv"
        # )
        assert isinstance(result, bytes)
        assert result == expected

    def test_obfuscate_file_ClientError(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")

        file_to_obfuscate = "s3://test-bucket/nonexistent.csv"
        pii_fields = ["sport"]

        with pytest.raises(ObfuscationError, match="S3 access failed"):
            obfuscate_file(file_to_obfuscate, pii_fields)

    def test_obfuscate_file_EmptyDataError(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="empty.csv", Body=""
        )  # empty content

        file_to_obfuscate = "s3://test-bucket/empty.csv"
        pii_fields = ["sport"]

        with pytest.raises(ObfuscationError, match="Input file is empty"):
            obfuscate_file(file_to_obfuscate, pii_fields)

    def test_obfuscate_file_ValueError(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        csv_data = "name,sport\nRonaldo,Football"
        s3_client.put_object(Bucket="test-bucket", Key="test-file.csv", Body=csv_data)

        file_to_obfuscate = "s3://test-bucket/test-file.csv"
        pii_fields = ["sport"]

        # Unsupported data_type (e.g., 'txt')
        with pytest.raises(ObfuscationError, match="Unsupported file type: txt"):
            obfuscate_file(file_to_obfuscate, pii_fields, data_type="txt")

    def test_obfuscate_file_TypeError(self):
        # --- Setup mock S3 environment ---
        s3 = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"
        key = "test-file.csv"
        s3.create_bucket(Bucket=bucket_name)

        # Create and upload a simple CSV file
        csv_data = "name,sport\nRonaldo,Football\nHamilton,F1\nNadal,Tennis"
        s3.put_object(Bucket=bucket_name, Key=key, Body=csv_data.encode())

        # --- Invalid pii_fields (should trigger TypeError inside obfuscate_df) ---
        invalid_pii_fields = "sport"  # not a list, should be list[str]

        # --- Run obfuscate_file and check behavior ---
        file_to_obfuscate = f"s3://{bucket_name}/{key}"

        with pytest.raises(
            ObfuscationError, match="`pii_fields` must be a list of strings."
        ):
            obfuscate_file(file_to_obfuscate, invalid_pii_fields, data_type="csv")

    def test_obfuscate_file_Exception(self, monkeypatch):
        # Setup mock S3 with valid CSV
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        csv_data = "name,sport\nRonaldo,Football"
        s3_client.put_object(Bucket="test-bucket", Key="test-file.csv", Body=csv_data)

        # Monkeypatch one of the internal calls to raise Exception
        monkeypatch.setattr(
            aws_gdpr_guard.obfuscator,
            "read_file_from_s3_bucket",
            lambda *a, **kw: (_ for _ in ()).throw(Exception("Unexpected error!")),
        )

        file_to_obfuscate = "s3://test-bucket/test-file.csv"
        pii_fields = ["sport"]

        with pytest.raises(ObfuscationError, match="Unexpected obfuscation error"):
            obfuscate_file(file_to_obfuscate, pii_fields)
