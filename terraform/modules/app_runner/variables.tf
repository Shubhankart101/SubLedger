variable "service_name" {
  description = "App Runner service name."
  type        = string
}

variable "ecr_repository_url" {
  description = "ECR repository URL containing the application image."
  type        = string
}

variable "image_tag" {
  description = "Existing image tag to deploy."
  type        = string
}

variable "app_env" {
  description = "Application environment value."
  type        = string
}

variable "database_url_secret_arn" {
  description = "Optional Secrets Manager ARN containing the database URL."
  type        = string
  default     = ""
}