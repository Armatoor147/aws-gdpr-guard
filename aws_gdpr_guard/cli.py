import argparse
from aws_gdpr_guard.obfuscator import obfuscate_file


def main():
    parser = argparse.ArgumentParser(description="AWS GDPR Guard CLI")
    parser.add_argument("s3_uri", type=str, help="S3 URI of the file to obfuscate")
    parser.add_argument(
        "--output", type=str, help="Output S3 URI for the obfuscated file", default=None
    )
    args = parser.parse_args()

    print(f"Obfuscating file at {args.s3_uri}...")
    obfuscate_file(args.s3_uri, args.output)
    print("Done!")


if __name__ == "__main__":
    main()
