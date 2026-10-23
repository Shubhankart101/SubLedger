data "aws_iam_policy_document" "ecr_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["build.apprunner.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecr_access" {
  name               = "${var.service_name}-apprunner-ecr-access"
  assume_role_policy = data.aws_iam_policy_document.ecr_assume_role.json
}

resource "aws_iam_role_policy_attachment" "ecr_access" {
  role       = aws_iam_role.ecr_access.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

data "aws_iam_policy_document" "instance_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["tasks.apprunner.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "instance" {
  name               = "${var.service_name}-apprunner-instance"
  assume_role_policy = data.aws_iam_policy_document.instance_assume_role.json
}

resource "aws_iam_role_policy" "database_secret" {
  count = var.database_url_secret_arn == "" ? 0 : 1
  name  = "${var.service_name}-database-secret-read"
  role  = aws_iam_role.instance.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = var.database_url_secret_arn
    }]
  })
}

resource "aws_apprunner_service" "this" {
  service_name = var.service_name

  source_configuration {
    auto_deployments_enabled = false

    authentication_configuration {
      access_role_arn = aws_iam_role.ecr_access.arn
    }

    image_repository {
      image_identifier      = "${var.ecr_repository_url}:${var.image_tag}"
      image_repository_type = "ECR"

      image_configuration {
        port = "8000"

        runtime_environment_variables = {
          APP_ENV = var.app_env
        }

        runtime_environment_secrets = var.database_url_secret_arn == "" ? {} : {
          DATABASE_URL = var.database_url_secret_arn
        }
      }
    }
  }

  instance_configuration {
    cpu               = "1 vCPU"
    memory            = "2 GB"
    instance_role_arn = aws_iam_role.instance.arn
  }

  depends_on = [aws_iam_role_policy_attachment.ecr_access]
}