module "ecr" {
  source       = "./modules/ecr"
  project_name = var.project_name
}

module "app_runner" {
  count  = var.enable_app_runner ? 1 : 0
  source = "./modules/app_runner"

  service_name           = var.project_name
  ecr_repository_url     = module.ecr.repository_url
  image_tag              = var.image_tag
  app_env                = var.app_env
  database_url_secret_arn = var.database_url_secret_arn
}