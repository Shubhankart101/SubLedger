# Pipeline Architecture

All workflows are in `.github/workflows/`.

## Automated Pull Request Validation

`pr-validation.yml` runs on pull requests targeting `main` and on pushes to `main`. It has independent jobs:

- **Python tests:** installs `requirements.txt` with Python 3.12 and runs `pytest`.
- **Terraform validation:** checks recursive formatting, initializes the AWS provider without configuring the remote backend, and runs `terraform validate`.

The workflow uses read-only repository permissions and needs no AWS credentials. Configure branch protection on `main` to require both jobs before merging; workflow definitions alone do not enforce a GitHub branch protection policy.

## Manual Build and Test

`manual-build-test.yml` is triggered from **Actions > Build and Test (Manual) > Run workflow**. It installs dependencies, runs tests, and builds a local Docker image tagged with the commit SHA. It does not push images or change infrastructure.

## Manual Deployment

`manual-deploy.yml` is triggered from **Actions > Deploy (Manual) > Run workflow**. It tests the checked-out commit, authenticates to AWS using GitHub OIDC, initializes Terraform state, creates the ECR repository if needed, builds/pushes the commit image, applies the App Runner service, and prints its URL.

Required GitHub configuration:

| Name | GitHub setting | Purpose |
| --- | --- | --- |
| `AWS_ROLE_ARN` | Repository or environment secret | IAM role assumed using OIDC |
| `AWS_REGION` | Repository variable | AWS resource region |
| `TF_STATE_BUCKET` | Repository variable | Pre-created S3 Terraform state bucket |
| `DATABASE_URL_SECRET_ARN` | Optional repository variable | ARN of Secrets Manager secret containing a PostgreSQL URL |

The AWS role trust policy should restrict the OIDC subject to this repository and the intended branch/environment. Grant only the ECR, App Runner, IAM role, and S3 state permissions needed by the deployment. Use a GitHub environment with required reviewers if manual production approval is needed.

## State and Deployment Behavior

The S3 backend uses a repository-specific state key, encryption, and native S3 lockfiles. The bucket must exist before the workflow runs. Terraform records the deployed image tag; automatic App Runner deployments from ECR are disabled. Each workflow run uses a unique immutable image tag built from the commit SHA and workflow run ID, so rerunning the same commit is supported.

The automated PR validation does not run `terraform apply`. Infrastructure mutation and cloud costs are restricted to the explicit manual deployment workflow.
