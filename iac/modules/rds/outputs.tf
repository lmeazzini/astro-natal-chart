# =============================================================================
# RDS Module - Outputs
# =============================================================================
# Outputs for use by application configuration and other modules.
# =============================================================================

output "endpoint" {
  description = "RDS instance endpoint (hostname)"
  value       = aws_db_instance.main.endpoint
}

output "address" {
  description = "RDS instance address (hostname without port)"
  value       = aws_db_instance.main.address
}

output "port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Name of the default database"
  value       = aws_db_instance.main.db_name
}

output "username" {
  description = "Master username"
  value       = aws_db_instance.main.username
}

output "password" {
  description = "Master password"
  value       = random_password.db.result
  sensitive   = true
}

output "connection_string" {
  description = "PostgreSQL connection string (asyncpg format)"
  value       = "postgresql+asyncpg://${aws_db_instance.main.username}:${random_password.db.result}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
  sensitive   = true
}

output "instance_id" {
  description = "RDS instance identifier"
  value       = aws_db_instance.main.id
}

output "instance_arn" {
  description = "RDS instance ARN"
  value       = aws_db_instance.main.arn
}

output "availability_zone" {
  description = "Availability zone of the RDS instance"
  value       = aws_db_instance.main.availability_zone
}
