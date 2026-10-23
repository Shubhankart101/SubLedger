output "service_url" {
  description = "Public App Runner URL."
  value       = "https://${aws_apprunner_service.this.service_url}"
}