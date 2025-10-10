# SSH key
resource "tls_private_key" "ec2_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# SSH key pair
resource "aws_key_pair" "ec2_key_pair" {
  key_name   = "aws-gdpr-guard-key-2"
  public_key = tls_private_key.ec2_key.public_key_openssh
}

# SSH key file
resource "local_file" "private_key" {
  filename        = "keys/aws_gdpr_guard_key.pem"
  content         = tls_private_key.ec2_key.private_key_pem
  file_permission = "0400"
}

# EC2 instance profile
resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2-instance-profile"
  role = aws_iam_role.aws_gdpr_guard_ec2_iam_role.name
}

# EC2 instance
resource "aws_instance" "aws_gdpr_guard_ec2_instance" {
  ami                         = "ami-04c08fd8aa14af291"
  instance_type               = "t3.micro"
  key_name                    = aws_key_pair.ec2_key_pair.key_name
  vpc_security_group_ids      = [aws_security_group.allow_ssh.id]
  subnet_id                   = aws_subnet.public.id
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.ec2_instance_profile.name

  tags = {
    Name = "aws-gdpr-guard-ec2-instance"
  }

  user_data = <<-EOF
        #!/bin/bash
        echo "S3_BUCKET_NAME=${local.bucket_name}" > /home/ec2-user/.env
    EOF

  provisioner "file" {
    source      = "${path.module}/aws_gdpr_guard.zip"
    destination = "aws_gdpr_guard.zip"
  }

  provisioner "file" {
    source      = "${path.module}/../ec2_script.py"
    destination = "ec2_script.py"
  }

  provisioner "file" {
    source      = "${path.module}/ec2_setup.sh"
    destination = "ec2_setup.sh"
  }

  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = tls_private_key.ec2_key.private_key_pem
    host        = self.public_ip
  }
}