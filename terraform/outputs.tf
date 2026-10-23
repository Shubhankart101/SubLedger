output "ecr_repository_url" {
  description = "ECR repository URL used by the manual image build and deploy workflow."
  value       = module.ecr.repository_url
}

output "app_runner_service_url" {
  description = "Public URL for the deployed App Runner service, or null before service creation."
  value       = var.enable_app_runner ? module.app_runner[0].service_url : null
}