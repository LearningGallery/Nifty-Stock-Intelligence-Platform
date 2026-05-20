terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Your default region provider
provider "aws" {
  region = var.aws_region
}

# Create a global region provider alias specifically for CloudFront WAF
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}