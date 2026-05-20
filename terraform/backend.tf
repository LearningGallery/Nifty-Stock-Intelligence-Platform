terraform {
  backend "s3" {
    bucket         = "nsip-terraform-state-${var.aws_account_id}"
    key            = "infrastructure/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    dynamodb_table = "nsip-terraform-locks"
    
    # Enable versioning for state file recovery
    versioning = true
  }
}
