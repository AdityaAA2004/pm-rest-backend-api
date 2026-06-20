terraform {
  backend "s3" {
    bucket         = "pm-rest-backend-api-tf-state"
    key            = "pm-rest-backend-api/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "pm-rest-backend-api-tf-lock"
    encrypt        = true
  }
}
