from setuptools import setup, find_packages

setup(
    name="aws-gdpr-guard",
    version="1.0.0",
    author="Vincent Toor-Azorin",
    author_email="vincent.toor@gmail.com",
    description="A Python package for anonymising PII in AWS S3 while ensuring GDPR compliance.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Armatoor147/aws-gdpr-guard",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.26.0,<2.0.0",
        "pandas>=2.0.0,<3.0.0",
        "pyarrow>=13.0.0,<22.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)