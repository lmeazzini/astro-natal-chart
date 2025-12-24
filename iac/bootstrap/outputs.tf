# =============================================================================
# Bootstrap Outputs
# =============================================================================
# Use these values to configure the backend in environments/*/backend.tf

output "state_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.id
}

output "state_bucket_arn" {
  description = "ARN of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.arn
}

output "state_bucket_region" {
  description = "Region of the S3 bucket"
  value       = data.aws_region.current.name
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_locks.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_locks.arn
}

output "account_id" {
  description = "AWS Account ID (for reference)"
  value       = data.aws_caller_identity.current.account_id
}

output "backend_config" {
  description = "Backend configuration to copy to environments/*/main.tf"
  value       = <<-EOT
    # Copy this to your environment's main.tf terraform block:
    backend "s3" {
      bucket         = "${aws_s3_bucket.terraform_state.id}"
      key            = "<environment>/terraform.tfstate"
      region         = "${data.aws_region.current.name}"
      encrypt        = true
      dynamodb_table = "${aws_dynamodb_table.terraform_locks.name}"
    }
  EOT
}
