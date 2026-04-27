variable "aws_region" {
  description = "AWS region for RDS deployment"
  type        = string
  default     = "us-east-1"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "appdb"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "appuser"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "app-eks-cluster"
}

variable "cluster_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "node_group_name" {
  description = "EKS node group name"
  type        = string
  default     = "app-node-group"
}

variable "node_group_instance_type" {
  description = "EKS node instance type"
  type        = string
  default     = "t3.small"
}

variable "node_group_desired_capacity" {
  description = "EKS node group desired capacity"
  type        = number
  default     = 2
}

variable "node_group_min_size" {
  description = "EKS node group minimum size"
  type        = number
  default     = 2
}

variable "node_group_max_size" {
  description = "EKS node group maximum size"
  type        = number
  default     = 4
}
