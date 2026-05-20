terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    # Backend configuration provided via backend.tf
  }
}
