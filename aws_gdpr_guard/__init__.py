"""
AWS GDPR Guard: A Python package for anonymising PII (Personally Identifiable Information)
stored in AWS S3, ensuring GDPR compliance by replacing sensitive data fields with obfuscated values.
"""

from .obfuscator import (
    split_s3_uri,
    read_file_from_s3_bucket,
    obfuscate_df,
    dataframe_to_bytes,
    obfuscate_file,
)

__all__ = [
    "split_s3_uri",
    "read_file_from_s3_bucket",
    "obfuscate_df",
    "dataframe_to_bytes",
    "obfuscate_file",
]
__version__ = "1.0.0"
