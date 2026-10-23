# SubLedger

SubLedger is a small SaaS billing backend for plans, customers, subscriptions, invoices, payment attempts, and append-only ledger events. Its code is split into API routes, Pydantic schemas, services, repositories, SQLAlchemy models, and database/configuration modules.

## Run Locally

Requires Python 3.11 or newer.

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive Swagger docs are at `/docs`. The default database is `./subledger.db`. Set `DATABASE_URL` to change it.

## Docker

```powershell
docker compose up --build
```

The service listens on port 8000 and persists its SQLite database in a named volume.

## Tests

```powershell
python -m pytest
```

## API Summary

| Method | Path | Purpose |
| --- | --- | --- |
| `POST`, `GET` | `/plans` | Create/list plans |
| `PUT` | `/plans/{plan_id}` | Update a plan |
| `POST` | `/plans/{plan_id}/deactivate` | Deactivate a plan |
| `POST`, `GET` | `/customers` | Create/list customers |
| `GET` | `/customers/{customer_id}` | Fetch a customer |
| `GET` | `/customers/{customer_id}/ledger` | Read customer ledger |
| `POST`, `GET` | `/subscriptions` | Create/list subscriptions |
| `PATCH` | `/subscriptions/{subscription_id}/cancel` | Cancel subscription |
| `POST` | `/invoices/generate` | Generate invoice from an active subscription |
| `GET` | `/invoices/{invoice_id}` | Fetch invoice |
| `POST` | `/payments/record` | Record successful or failed payment attempt |

Amounts use decimal currency values with two fractional digits. Payment `status` is `success` or `failed`; billing cycle is `monthly` or `yearly`. Invoice periods can be omitted to use the subscription's next billing date, or supplied as a start/end pair.

## Design

See [DESIGN.md](DESIGN.md) for the ERD, service and repository responsibilities, business-rule ownership, Repository Pattern rationale, and invoice/payment flows.

## Documentation

Detailed project documentation lives in [`docs/`](docs/README.md), including application architecture, API behavior, local development, testing, CI/CD workflows, and AWS deployment.

## GitHub Actions

- Pull requests and pushes to `main` run automated application tests and Terraform formatting/validation.
- `Build and Test (Manual)` builds and tests the container without deploying it.
- `Deploy (Manual)` tests the code, bootstraps the ECR repository, pushes the selected commit image, and applies the App Runner Terraform configuration.

Configure GitHub Actions with an AWS OIDC role ARN secret named `AWS_ROLE_ARN`, repository variables `AWS_REGION` and `TF_STATE_BUCKET`, and an S3 state bucket configured for Terraform state locking. See [`docs/pipelines.md`](docs/pipelines.md) and [`docs/terraform-deployment.md`](docs/terraform-deployment.md) before running these workflows.

## Scope and Limitations

There is no real payment-gateway integration, authentication/RBAC, tax calculation, proration, refunds, or background recurring-billing scheduler. Invoice generation is an explicit API action. The App Runner Terraform module is a basic service deployment, not a complete production platform; configure an external persistent PostgreSQL database through AWS Secrets Manager instead of relying on the default ephemeral SQLite file. This starter uses `create_all`; production deployments should add Alembic migrations, hardened database permissions for ledger immutability, and concurrency controls appropriate to their database.
