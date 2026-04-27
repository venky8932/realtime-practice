output "db_endpoint" {
  description = "RDS endpoint for the PostgreSQL database"
  value       = aws_db_instance.app_db.endpoint
}

output "db_port" {
  description = "PostgreSQL port"
  value       = aws_db_instance.app_db.port
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.app_db.name
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.app.name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.app.endpoint
}

output "eks_cluster_certificate_authority_data" {
  description = "EKS cluster certificate authority data"
  value       = aws_eks_cluster.app.certificate_authority[0].data
}
