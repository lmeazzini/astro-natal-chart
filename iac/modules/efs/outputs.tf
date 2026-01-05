# =============================================================================
# EFS Module - Outputs
# =============================================================================

output "file_system_id" {
  description = "ID of the EFS file system"
  value       = aws_efs_file_system.main.id
}

output "file_system_arn" {
  description = "ARN of the EFS file system"
  value       = aws_efs_file_system.main.arn
}

output "access_point_id" {
  description = "ID of the EFS access point for Qdrant"
  value       = aws_efs_access_point.qdrant.id
}

output "access_point_arn" {
  description = "ARN of the EFS access point for Qdrant"
  value       = aws_efs_access_point.qdrant.arn
}

output "mount_target_id" {
  description = "ID of the EFS mount target"
  value       = aws_efs_mount_target.main.id
}

output "mount_target_dns_name" {
  description = "DNS name of the EFS mount target"
  value       = aws_efs_mount_target.main.dns_name
}
