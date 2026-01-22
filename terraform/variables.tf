variable "region" {
  description = "AWS region"
  type        = string
}

variable "postgres_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

variable "public_key_path" {
  description = "Path to public key"
  type        = string
}
