output "vpc_id" {
  description = "ID of the VPC created for Notes App"
  value       = aws_vpc.notes_vpc.id
}

output "public_ip" {
  description = "Public IP address of the deployed compute instance"
  value       = aws_instance.notes_host.public_ip
}

output "app_url" {
  description = "Public URL for Notes Application"
  value       = "http://${aws_instance.notes_host.public_ip}:5000"
}

output "prometheus_url" {
  description = "Public URL for Prometheus Monitoring"
  value       = "http://${aws_instance.notes_host.public_ip}:9090"
}

output "grafana_url" {
  description = "Public URL for Grafana Dashboards"
  value       = "http://${aws_instance.notes_host.public_ip}:3000"
}
