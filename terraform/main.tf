provider "aws" {
  region = var.region
}

# VPC & Subnets (default kullanıyoruz)
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Group - EC2
resource "aws_security_group" "ec2_sg" {
  name        = "ats-ec2-sg2"
  description = "Allow HTTP and SSH"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Daha iyi: kendi IP'niz
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security Group - RDS
resource "aws_security_group" "rds_sg" {
  name        = "ats-rds-sg2"
  description = "Allow PostgreSQL from EC2"

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  vpc_id = data.aws_vpc.default.id
}

# RDS Instance
resource "aws_db_instance" "ats_db" {
  identifier           = "ats-db"
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t4g.micro"
  allocated_storage    = 20
  username             = "postgres"
  password             = var.postgres_password
  publicly_accessible  = false
  skip_final_snapshot  = true
  db_name              = "ats_system"
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name = aws_db_subnet_group.default.name
}

resource "aws_db_subnet_group" "default" {
  name       = "ats-db-subnet-group"
  subnet_ids = slice(data.aws_subnets.default.ids, 0, 2)
}

# Subnet bilgisi için data source
data "aws_subnet" "selected" {
  id = data.aws_subnets.default.ids[0]
}

# EBS Volume
resource "aws_ebs_volume" "chroma_data" {
  availability_zone = data.aws_subnet.selected.availability_zone
  size              = 5
  type              = "gp2"
  tags = {
    Name = "chroma-data"
  }
}

# EC2 Instance
resource "aws_key_pair" "deployer" {
  key_name   = "ats-key"
  public_key = file(var.public_key_path)
}

data "aws_ami" "amazon_linux_arm" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-arm64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "ats_app" {
  ami                    = data.aws_ami.amazon_linux_arm.id
  instance_type          = "t4g.micro"
  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  subnet_id              = data.aws_subnets.default.ids[0]

  root_block_device {
    volume_size = 8
  }

  tags = {
    Name = "ats-app"
  }

  user_data = <<-EOF
              #!/bin/bash
              mkfs -t ext4 /dev/xvdh
              mkdir -p /mnt/ebs
              mount /dev/xvdh /mnt/ebs
              chown ubuntu:ubuntu /mnt/ebs
              echo '/dev/xvdh /mnt/ebs ext4 defaults,nofail 0 2' >> /etc/fstab
              EOF
}

# EBS'yi EC2'ya attach et
resource "aws_volume_attachment" "ebs_att" {
  device_name = "/dev/xvdh"
  volume_id   = aws_ebs_volume.chroma_data.id
  instance_id = aws_instance.ats_app.id
}
