# Security group
resource "aws_security_group" "allow_ssh" {
    name = "allow_ssh"
    description = "Allow SSH and outbound traffic"
    vpc_id      = aws_vpc.main.id

    # Ingress: Only allow SSH from local IP
    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = [var.my_ip]
    }

    # Egress: Allow all outbound traffic
    egress {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
}