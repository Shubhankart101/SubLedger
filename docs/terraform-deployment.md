# Terraform and AWS Deployment

## Infrastructure

Terraform lives in `terraform/` and is split into reusable modules:

- `modules/ecr` provisions an encrypted, immutable ECR repository, on-push image scanning, and cleanup of untagged images older than 30 days.
- `modules/app_runner` provisions the ECR access role, App Runner instance role, optional Secrets Manager read permission, and public App Runner service.
- Root Terraform wires modules together and exposes the ECR URL and service URL.

The service defaults to disabled so the ECR repository can be created before an image exists. App Runner auto-deploy from ECR is disabled; the manual pipeline applies each selected commit SHA.

## One-Time AWS Setup

1. Create an S3 bucket for Terraform state in the target region. Enable bucket versioning and server-side encryption; restrict access to the GitHub deployment role. The workflow uses S3 native state locking (`use_lockfile`) and Terraform 1.10+.
2. Configure an AWS IAM OIDC provider for GitHub Actions and create a role whose trust condition is restricted to this repository and intended deployment branch/environment.
3. Grant that role the required ECR repository/image, App Runner service, limited IAM role/policy, and state bucket read/write permissions. Avoid broad administrator policies for routine operation.
4. Add GitHub Actions variables `AWS_REGION` and `TF_STATE_BUCKET`, plus secret `AWS_ROLE_ARN`.
5. For persistent production data, create a PostgreSQL database outside this starter stack and store a SQLAlchemy URL in AWS Secrets Manager. Set `DATABASE_URL_SECRET_ARN` to its ARN. The URL should use `postgresql+psycopg://`.
6. Run **Deploy (Manual)** from GitHub Actions.

The workflow first applies only the ECR module, then pushes the selected commit image, then applies the complete configuration to create/update App Runner. This sequencing avoids attempting to deploy a container image that does not yet exist.

## Local Terraform Commands

Install Terraform 1.10 or newer and configure AWS credentials with least privilege. Use a temporary local state only for isolated development; do not mix local state with the CI S3 state.

```powershell
terraform -chdir=terraform fmt -recursive
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
```

To inspect a plan against the remote backend, supply the same S3 backend settings used by CI and use `terraform plan`. Do not run apply against shared or production infrastructure outside the reviewed manual workflow.

## Costs and Limitations

AWS ECR storage and App Runner compute incur charges. This stack does not create a VPC, database, DNS, TLS certificate, WAF, alarms, or backups. App Runner is publicly reachable. Without `DATABASE_URL_SECRET_ARN`, the app uses SQLite inside the container, which is ephemeral and unsuitable for production billing records. Configure an external PostgreSQL database before production use.
