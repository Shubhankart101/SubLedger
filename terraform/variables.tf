variable "aws_region" {
  description = "AWS region for the SubLedger service."
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Short lowercase name used to create AWS resources."
  type        = string
  default     = "subledger"
}

variable "enable_app_runner" {
  description = "Create the App Runner service after its image has been pushed to ECR."
  type        = bool
  default     = false
}

variable "image_tag" {
  description = "Existing ECR image tag to deploy."
  type        = string
  default     = "latest"
}

variable "app_env" {
  description = "Application environment value passed to the container."
  type        = string
  default     = "production"
}

variable "database_url_secret_arn" {
  description = "Optional Secrets Manager ARN containing the SQLAlchemy database URL."
  type        = string
  default     = ""
}