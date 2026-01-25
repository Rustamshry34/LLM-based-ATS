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

# Ubuntu 22.04 LTS (Jammy) - x86_64
data "aws_ami" "ubuntu_x86_64" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

resource "aws_instance" "ats_app" {
  ami                    = data.aws_ami.ubuntu_x86_64.id
  instance_type          = "t3.micro"
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
set -e

LOG=/var/log/ats-init.log
echo "Init started at $(date)" >> $LOG

DISK="/dev/nvme1n1"

# Disk gelene kadar bekle
while [ ! -b "$DISK" ]; do
  echo "Waiting for EBS disk..." >> $LOG
  sleep 2
done

# Dosya sistemi yoksa formatla
if ! blkid $DISK; then
  mkfs.ext4 $DISK
fi

mkdir -p /mnt/ebs

# Mount et (değilse)
if ! mountpoint -q /mnt/ebs; then
  mount $DISK /mnt/ebs
fi

# Kalıcı hale getir
grep -q "$DISK" /etc/fstab || echo "$DISK /mnt/ebs ext4 defaults,nofail 0 2" >> /etc/fstab

chown ubuntu:ubuntu /mnt/ebs

echo "EBS mounted successfully" >> $LOG
}

# EBS'yi EC2'ya attach et
resource "aws_volume_attachment" "ebs_att" {
  device_name = "/dev/xvdh"
  volume_id   = aws_ebs_volume.chroma_data.id
  instance_id = aws_instance.ats_app.id

  depends_on = [aws_instance.ats_app]
}
