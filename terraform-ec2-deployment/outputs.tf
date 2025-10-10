# EC2 instance public IP
output "ec2_instance_public_ip" {
  value = aws_instance.aws_gdpr_guard_ec2_instance.public_ip
}