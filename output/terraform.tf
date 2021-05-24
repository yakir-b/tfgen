
terraform {
  required_version               = "~> 0.14.0"
  
  backend "s3" {
    bucket = "prod-use1-terraform-backend"
    key = "terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "prod-use1-terraform-lock"
  }

}
