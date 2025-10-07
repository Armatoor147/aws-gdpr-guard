output "ec2_instance_public_ip" {
    value = aws_instance.aws_gdpr_guard-EC2-instance.public_ip
}