# terraform/backend.tf
terraform {
  backend "s3" {
    bucket         = "terraform-remote-state4"
    key            = "ats/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
