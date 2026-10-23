output "repository_url" {
  description = "URL of the ECR image repository."
  value       = aws_ecr_repository.this.repository_url
}