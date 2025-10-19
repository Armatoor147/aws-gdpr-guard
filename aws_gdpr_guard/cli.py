import argparse
import boto3
from aws_gdpr_guard.obfuscator import obfuscate_file


def main():
    parser = argparse.ArgumentParser(description="AWS GDPR Guard CLI")
    parser.add_argument("s3_uri", type=str, help="S3 URI of the file to obfuscate")
    parser.add_argument(
        "--output", type=str, help="Output S3 URI for the obfuscated file", default=None
    )
    parser.add_argument(
        "--pii-fields", nargs="+", required=True, help="List of PII fields to obfuscate"
    )
    parser.add_argument("--data-type", type=str, default="csv", help="Type of the file (csv, json, or parquet). Defaults to 'csv'.")
    args = parser.parse_args()

    print(f"Obfuscating file at {args.s3_uri}...")
    obfuscated_data = obfuscate_file(args.s3_uri, args.pii_fields, args.data_type)
    print("Obfuscation complete!")

    if args.output:
        output_bucket, output_key = args.output.replace("s3://", "").split("/", 1)
        s3_client = boto3.client("s3")
        s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=obfuscated_data)
        print(f"Uploaded obfuscated data to {args.output}")
    else:
        print("Obfuscated data (first 100 bytes):", obfuscated_data[:100])


if __name__ == "__main__":
    main()
