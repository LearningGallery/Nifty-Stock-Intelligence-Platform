provider "aws" {
  region = "ap-south-1"
}

# 1. The S3 Bucket
resource "aws_s3_bucket" "terraform_state" {
  bucket = "nsip-terraform-state-123456789012" # Ensure this is unique
  force_destroy = true # Caution: This will delete the bucket and all its contents when the infrastructure is destroyed
}

# 2. Enable Versioning (Crucial for state recovery)
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 3. Server-Side Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 4. DynamoDB for State Locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}