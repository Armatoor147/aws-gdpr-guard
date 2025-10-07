# SSH Key Pair
resource "tls_private_key" "ec2_key" {
    algorithm = "RSA"
    rsa_bits  = 4096
}

resource "aws_key_pair" "ec2_key_pair" {
    key_name   = "aws_gdpr_guard_key_2"
    public_key = tls_private_key.ec2_key.public_key_openssh
}

resource "local_file" "private_key" {
    filename        = "keys/aws_gdpr_guard_key.pem"
    content         = tls_private_key.ec2_key.private_key_pem
    file_permission = "0400"
}

# EC2 Instance
resource "aws_instance" "aws_gdpr_guard-EC2-instance" {
    ami = "ami-04c08fd8aa14af291"
    instance_type = "t3.micro"
    key_name = aws_key_pair.ec2_key_pair.key_name
    vpc_security_group_ids = [aws_security_group.allow_ssh.id]
    subnet_id = aws_subnet.public.id
    associate_public_ip_address = true

    tags = {
        Name = "aws_gdpr_guard-EC2-instance"
    }

    provisioner "file" {
        source = "${path.module}/aws_gdpr_guard.zip"
        destination = "aws_gdpr_guard.zip"
    }

    provisioner "file" {
        source = "${path.module}/../ec2_script.py"
        destination = "ec2_script.py"     
    }

    provisioner "file" {
        source = "${path.module}/ec2_setup.sh"
        destination = "ec2_setup.sh"
    }
    
    connection {
        type = "ssh"
        user = "ec2-user"
        private_key = tls_private_key.ec2_key.private_key_pem
        host = self.public_ip
    }
}