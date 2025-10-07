from aws_gdpr_guard.obfuscator import obfuscate_file
import os


def lambda_handler(event, context):
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    file_to_obfuscate = (f"s3://{S3_BUCKET_NAME}/dummy_students.csv")
    pii_fields = ["name", "email_address"]
    bytes_data = obfuscate_file(file_to_obfuscate, pii_fields)
    return bytes_data