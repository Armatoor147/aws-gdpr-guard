from aws_gdpr_guard.obfuscator import obfuscate_file
import os


def main():
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    file_to_obfuscate = f"s3://{S3_BUCKET_NAME}/dummy_students.csv"
    pii_fields = ["name", "email_address"]
    file_type = "csv"
    bytes_data = obfuscate_file(file_to_obfuscate, pii_fields, file_type)
    print(bytes_data)


if __name__ == "__main__":
    main()
