# Use Python 3.12
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the library and the script to the container
COPY aws_gdpr_guard/ ./aws_gdpr_guard/
COPY ecs_script.py .

# Install dependencies
RUN pip install --no-cache-dir -r aws_gdpr_guard/requirements.txt

# Command to run the script
CMD ["python", "ecs_script.py"]