#!/bin/bash

# Store local IP address
touch terraform.tfvars
MY_IP=$(curl -4 -s ifconfig.me)/32
echo "my_ip = \"$MY_IP\"" > terraform.tfvars

# Zip package
zip -r aws_gdpr_guard.zip ../aws_gdpr_guard/