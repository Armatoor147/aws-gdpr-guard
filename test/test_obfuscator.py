from aws_gdpr_guard.obfuscator import split_S3_URI, read_CSV_file_from_S3_bucket, obfuscate_df, obfuscate_file
import pytest
from unittest.mock import MagicMock, Mock, patch
from io import StringIO
import pandas as pd
from botocore.exceptions import ClientError


class Test_split_S3_URI:
    def test_split_S3_URI_sucessful(self):
        s3_uri = "s3://test-bucket/test-file.csv"
        expected_bucket_name = "test-bucket"
        expected_object_name = "test-file.csv"
        bucket_name, object_name = split_S3_URI(s3_uri)
        assert bucket_name == expected_bucket_name
        assert object_name == expected_object_name
    
    def test_split_S3_URI_ValueError(self):
        s3_uri = "s2://test-bucket/test-file.csv"
        with pytest.raises(ValueError, match="Invalid S3 URI format"):
            split_S3_URI(s3_uri)


class Test_read_CSV_file_from_S3_bucket:
    def test_read_CSV_file_from_S3_bucket_successful(self):
        test_csv_data = "name,sport\nRonaldo,Football\nHamilton,F1\nNadal,Tennis"
        expected = pd.DataFrame({"name": ["Ronaldo", "Hamilton", "Nadal"], "sport": ["Football", "F1", "Tennis"]})
        
        test_bucket = "test-bucket"
        test_object = "test-file.csv"

        mock_streaming_body = StringIO(test_csv_data)
        mock_s3_client = MagicMock()
        mock_s3_client.get_object.return_value = {"Body": mock_streaming_body}

        result = read_CSV_file_from_S3_bucket(mock_s3_client, test_bucket, test_object)
        
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, expected)
        mock_s3_client.get_object.assert_called_once_with(Bucket=test_bucket, Key=test_object)
    
    def test_read_CSV_file_from_S3_bucket_ClientError(self):
        mock_s3_client = MagicMock()
        test_bucket = "test-bucket"
        test_object = "test-file.csv"
        mock_s3_client.get_object.side_effect = ClientError(
            error_response={"Error": {"Code": "404", "Message": "S3 access issue"}},
            operation_name="GetObject"
        )
        with pytest.raises(ClientError, match="S3 access issue"):
            read_CSV_file_from_S3_bucket(mock_s3_client, test_bucket, test_object)

    def test_read_CSV_file_from_S3_bucket_EmptyDataError(self):
        mock_s3_client = MagicMock()
        mock_s3_client.get_object.return_value = {"Body": StringIO("")}
        test_bucket = "test-bucket"
        test_object = "test-file.csv"
        with pytest.raises(pd.errors.EmptyDataError, match="CSV file is empty"):
            read_CSV_file_from_S3_bucket(mock_s3_client, test_bucket, test_object)
    
    def test_read_CSV_file_from_S3_bucket_Exception(self):
        mock_s3_client = MagicMock()
        mock_s3_client.get_object.side_effect = RuntimeError
        test_bucket = "test-bucket"
        test_object = "test-file.csv"
        with pytest.raises(Exception):
            read_CSV_file_from_S3_bucket(mock_s3_client, test_bucket, test_object)


class Test_obfuscate_df:
    def test_obfuscate_df_successful(self):
        data = pd.DataFrame({"name": ["Ronaldo", "Hamilton", "Nadal"], "sport": ["Football", "F1", "Tennis"]})
        pii_fields = ["sport"]
        expected = pd.DataFrame({"name": ["Ronaldo", "Hamilton", "Nadal"], "sport": ["***", "***", "***"]})
        result = obfuscate_df(data, pii_fields)
        pd.testing.assert_frame_equal(result, expected)
    
    def test_obfuscate_df_TypeError_data(self):
        data = "Not a pd.DataFrame"
        pii_fields = ["sports"]
        with pytest.raises(TypeError, match="`data` must be a pandas DataFrame."):
            obfuscate_df(data, pii_fields)

    def test_obfuscate_df_TypeError_pii_fields(self):
        data = pd.DataFrame({"name": ["Ronaldo", "Hamilton", "Nadal"], "sport": ["Football", "F1", "Tennis"]})
        pii_fields = ["sports", 1234]
        with pytest.raises(TypeError, match="`pii_fields` must be a list of strings."):
            obfuscate_df(data, pii_fields)

    def test_obfuscate_df_ValueError(self):
        data = pd.DataFrame({"name": ["Ronaldo", "Hamilton", "Nadal"], "sport": ["Football", "F1", "Tennis"]})
        pii_fields = ["age"]
        expected_match = r"Columns not found in DataFrame: \{\'age\'\}. Available columns: \['name', 'sport'\]"
        with pytest.raises(ValueError, match=expected_match):
            obfuscate_df(data, pii_fields)

@patch("aws_gdpr_guard.obfuscator.boto3.client")
class Test_obfuscate_file:
    def test_obfuscate_file_successful(self, mock_boto3_client):
        file_to_obfuscate = "s3://test-bucket/test-file.csv"
        pii_fields = ["sport"]

        mock_s3_client = Mock()
        test_csv_data = "name,sport\nRonaldo,Football\nHamilton,F1\nNadal,Tennis"
        mock_s3_response = {"Body": StringIO(test_csv_data)}
        mock_s3_client.get_object.side_effect = lambda Bucket, Key: (
            mock_s3_response if (Bucket, Key) == ("test-bucket", "test-file.csv")
            else Exception(f"Unexpected call with Bucket={Bucket}, Key={Key}")
        )
        mock_boto3_client.return_value = mock_s3_client

        result = obfuscate_file(file_to_obfuscate, pii_fields)

        mock_boto3_client.assert_called_once_with("s3")
        mock_s3_client.get_object.assert_called_once_with(
            Bucket="test-bucket", 
            Key="test-file.csv"
        )
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 2)
        assert result["name"].tolist() == ["Ronaldo", "Hamilton", "Nadal"]
        assert result["sport"].tolist() == ["***", "***", "***"]




    # Test every type of error in obfuscate_file !!!
