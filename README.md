# GDPR Obfuscator Project

## Project Description

### Core requirements

#### 1) Purpose

- Build a Python library to anonymise PII (Personally Identifiable Information) stored in AWS S3.
- Ensure GDPR compliance by replacing sensitive data fields (e.g. names, emails) with obfuscated values (e.g. `***`).


#### 2) Input/Output

- **Input**: JSON config with:
	- S3 file path
	- List of PII fields
- **Output**: Byte stream of the obfuscated file (compatible with `boto3.S3.PutObject`).


#### 3) File Handling

- **MVP**: CSV support only.
- **Future**: Extend to JSON/Parquet.


### Technical Specification

- **Language**: Python (PEP-8 compliant, unit-tested).
- **AWS Integration**: Use `boto3` for S3 access. No hardcoded credentials.
- **Performance**: Handle 1MB files in <1 minute.
- **Deployment**: Lambda/ECS/EC2 (memory-efficient for Lambda).
- **Security**: Scan for vulnerabilities; document code.


### Key Assumptions

- PII fields are pre-identified.
- Data includes a primary key.
- Invocation via AWS services (e.g. EventBridge) is optional for the MVP. 


## Project Architecture

This project consists of the following components:

### **Python Library**: Core logic for GDPR data obfuscation.

The `aws_gdpr_guard` python library includes the main obfuscator function `obfuscate_file` inside `aws_gdpr_guard.obfuscator.py` that uses the following utility functions:
- `split_s3_uri`: Splits S3 URIs into bucket and key.
- `read_file_from_s3_bucket`: Reads files from S3 bucket (CSV, JSON or Parquet).
- `obfuscate_df`: Obfuscates DataFrame columns.
- `dataframe_to_bytes`: Converts DataFrame to byte strings.

To make the library usable as both a pip-installable package and a command-line tool, I implemented two additional components: The `setup.py` file defines the package metadata, dependencies, and entry points, enabling users to install the library via pip and register the aws-gdpr-guard CLI command. The `cli.py` script provides a user-friendly command-line interface, allowing users to invoke the obfuscation logic directly from the terminal—either to preview obfuscated data or upload results to S3. Together, these components bridge the gap between the core library logic and practical, real-world usage.


### **Pytest Suite**: Unit and integration tests for the library.

1) Unit testing: Validate the individual utility functions.
2) Integration testing: Ensure the obfuscation works from start to end.
3) Error/Exception handling: Simulate every possible error that could occur.
4) Coverage: Verify every statement from the source code runs as espected.


### **CI/CD Pipeline**: Automated testing and deployment workflows.

Setup:
- Set up virtual environment
- Install requirements (from requirements-dev.txt)

Checks:
- Code quality:
    - black: Code formatter (ensures PEP 8-compliance and consistent style)
    - bandit: Security linter (scans Python code for common security vulnerabilities)
- Testing
    - pytest: Testing framework (ensures the source code functions as expected)
    - coverage: Coverage-measuring tool (measures the percentage of executable statements covered by unit tests)
- Security
    - pip-audit: Package security tool (scans the Python environment's dependencies for known security vulnerabilities)


### **Infrastructure as Code (IaC)**: Terraform modules for deploying the library.

- AWS Lambda (serverless)
- EC2 (VMs)
- ECS (containers)


## GitHub Repository Structure

```
aws-gdpr-guard
├── aws_gdpr_guard/                 # Core Python library for GDPR-compliant PII
│   ├── __init__.py
│   ├── obfuscator.py
│   ├── cli.py
│   ├── requirements.txt            # Production dependencies
├── tests/                          # Unit and integration tests (pytest)
│   ├── test_obfuscator.py
├── setup.py                        # Package metadata and installation configuration
├── Makefile                        # Common development tasks
├── .github/workflows/deploy.yml    # GitHub Actions CI/CD Pipeline
├── terraform-lambda-deployment     # Lambda deployment
├── terraform-ec2-deployment        # EC2 deployment
├── terraform-ecs-deployment        # ECS deployment
├── Dockerfile                      # Containerization for ECS
├── .dockerignore                   # Files to exclude from Docker builds
├── ec2_script.py                   # EC2 deployment script
├── lambda_function.py              # AWS Lambda function
├── ecs_script.py                   # ECS deployment script
├── local_script.py                 # Local deployment script
├── local_script_for_testing_1MB.py # Script for performance testing
├── dummy_data/                     # Dummy data (CSV, JSON, Parquet)
├── .gitignore                      # Files/dirs to exclude from Git
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
├── requirements.in                 # Top-level dependencies
├── docs/                           # Deployment documentation
├── LICENSE                         # Project license (MIT)
└── README.md                       # Project overview and instructions
```


## Development Plan

The project was developed in the following phases:

1. Designed and implemented the Python library and pytest suite.
2. Set up a CI/CD pipeline using Makefile and GitHub Actions to automate testing and ensure code quality.
3. Manually deployed the library to AWS Lambda, EC2, and ECS to validate compatibility.
4. Translated the infrastructure into Terraform modules for automated deployments.


## Implementation

Have a look at `/docs`:

* Option A: [Local Testing](docs/local.md)

* Option B: [CLI](docs/cli.md)

* Option C: [AWS Lambda](docs/lambda.md)

* Option D: [EC2](docs/ec2.md)

* Option E: [ECS](docs/ecs.md)



## Performance Testing

The `obfuscate_file` function was tested with CSV files of different sizes to evaluate its efficiency:

- ~1KB file: The function executed in ~0.5 seconds.
- ~1MB file: The function executed in ~1.5 seconds, well under the 1-minute requirement.


# Quality Assurance and CI/CD Validation

The GitHub Actions CI/CD pipeline successfully executed all checks:

The GitHub Actions CI/CD pipeline successfully executed all checks:
   Check      | Result                                                                 |
 |------------|------------------------------------------------------------------------|
 | black      | 4 files would be left unchanged (style enforced)                       |
 | bandit     | No issues identified (215 lines scanned)                               |
 | pytest     | All 24 tests passed in 2.95s                                           |
 | coverage   | 100% coverage (294 statements, 0 missed)                               |
 | pip-audit  | No known vulnerabilities found  


---
## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
