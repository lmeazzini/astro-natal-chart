# =============================================================================
# ECR Module - Outputs
# =============================================================================
# Exports repository information and IAM policy ARNs.
# =============================================================================

# -----------------------------------------------------------------------------
# Repository Information
# -----------------------------------------------------------------------------

output "repository_url" {
  description = "Full URL of the ECR repository (for docker push/pull)"
  value       = aws_ecr_repository.main.repository_url
}

output "repository_arn" {
  description = "ARN of the ECR repository"
  value       = aws_ecr_repository.main.arn
}

output "repository_name" {
  description = "Name of the ECR repository"
  value       = aws_ecr_repository.main.name
}

output "registry_id" {
  description = "The registry ID where the repository was created"
  value       = aws_ecr_repository.main.registry_id
}

# -----------------------------------------------------------------------------
# IAM Policies
# -----------------------------------------------------------------------------

output "push_policy_arn" {
  description = "ARN of the IAM policy for pushing images (attach to CI/CD role)"
  value       = aws_iam_policy.ecr_push.arn
}

output "pull_policy_arn" {
  description = "ARN of the IAM policy for pulling images (attach to ECS execution role)"
  value       = aws_iam_policy.ecr_pull.arn
}

# -----------------------------------------------------------------------------
# Convenience Outputs
# -----------------------------------------------------------------------------

output "docker_login_command" {
  description = "AWS CLI command to login to ECR"
  value       = "aws ecr get-login-password --region ${data.aws_region.current.name} | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com"
}

output "docker_push_command" {
  description = "Example docker push command (replace TAG)"
  value       = "docker push ${aws_ecr_repository.main.repository_url}:TAG"
}
