#!/bin/bash

# Update yum
sudo yum update

# Install Python3.12 and set it as main Python version
sudo yum install -y python3.12 python3-pip
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 2
sudo alternatives --set python3 /usr/bin/python3.12

# Install PIP and set Python3.12 as default for PIP
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
sudo ln -sf /usr/local/bin/pip3.12 /usr/bin/pip

# Unzip ZIP file containing the library
unzip aws_gdpr_guard.zip

# Create virtual environment and install dependencies
python3.12 -m venv venv
source venv/bin/activate
pip3 install -r aws_gdpr_guard/requirements.txt