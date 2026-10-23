# Security and Operations

## Secrets and Identity

- Never put AWS access keys, database passwords, or `.env` contents in source control.
- GitHub deployment uses OIDC; restrict the AWS trust policy by repository, branch, and preferably GitHub environment.
- Store the database URL in AWS Secrets Manager. The App Runner instance role receives only `GetSecretValue` for that secret ARN.
- Terraform state can contain infrastructure metadata and secret references. Protect the S3 bucket, enable versioning/encryption, and limit read/write access to the deployment role.

## Data Safety

The local SQLite configuration is for development only. In App Runner, local files are not a durable billing database. Use a managed PostgreSQL service and configure `DATABASE_URL_SECRET_ARN` before accepting real customer or ledger data.

Ledger entries are append-only through this application’s repository/service surface, but this does not make the database tamper-proof. Production systems should additionally enforce database permissions, backups, monitoring, and auditable retention.

## Production Readiness Gaps

- Add Alembic migrations and a controlled migration job before schema changes.
- Add authentication/authorization, rate limits, request tracing, structured logs, and alerting.
- Add database backups, restore drills, concurrency controls, and idempotency policy for payment requests.
- Use a payment provider integration and webhook signature validation rather than trusting client-reported payment status.
- Review AWS IAM policy scope, App Runner ingress, data residency, and retention requirements for the target organization.
