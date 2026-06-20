variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "pm-rest-backend-api"
}

variable "db_password" {
  type      = string
  sensitive = true
  description = "PostgreSQL master password for the RDS instance."
}

variable "ecr_image_tag" {
  type    = string
  default = "latest"
  description = "Docker image tag to deploy from ECR."
}

variable "jwt_secret" {
  type      = string
  sensitive = true
  description = "JWT signing secret. Set via terraform.auto.tfvars.json — never hardcode."
}
