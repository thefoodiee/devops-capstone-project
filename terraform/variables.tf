variable "aws_region" {
  description = "AWS region for infrastructure provisioning"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "production"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "notes-app"
}

variable "vpc_cidr" {
  description = "CIDR block for the Virtual Private Cloud (VPC)"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "instance_type" {
  description = "EC2 instance size for the node"
  type        = string
  default     = "t3.medium"
}
