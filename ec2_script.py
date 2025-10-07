from aws_gdpr_guard.obfuscator import obfuscate_file, split_S3_URI, read_CSV_file_from_S3_bucket, obfuscate_df
import boto3


def main():
    file_to_obfuscate = "s3://vincent-toor-azorin-aws-gdpr-guard-test-bucket/dummy_students.csv"
    pii_fields = ["name", "email_address"]
    # bytes_data = obfuscate_file(file_to_obfuscate, pii_fields)
    # print(bytes_data)

    print("Hey 1")
    # Extract bucket name and object name from the S3 URI
    bucket_name, object_name = split_S3_URI(file_to_obfuscate)
    print("Hey 2")
    # Connect to S3 client
    s3_client = boto3.client("s3")
    print("Hey 3")
    # Save S3 bucket (CSV) file as a table variable
    data_df = read_CSV_file_from_S3_bucket(s3_client, bucket_name, object_name)
    print("Hey 4")
    # Obfuscate relevant columns
    obfuscated_data_df = obfuscate_df(data_df, pii_fields)
    print("Hey 5")
    # Turn dataframe to bytes
    bytes_data = obfuscated_data_df.to_csv(index=False).encode()
    print("Hey 6")

if __name__ == "__main__":
    main()