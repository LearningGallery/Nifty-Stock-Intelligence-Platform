terraform {
  backend "s3" {
    bucket         = "nsip-terraform-state-123456789012"
    key            = "infrastructure/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
  }
}
