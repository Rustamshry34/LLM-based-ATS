output "ec2_public_ip" {
  value = aws_instance.ats_app.public_ip
}

output "rds_endpoint" {
  value = aws_db_instance.ats_db.endpoint
}
