# SubLedger Documentation

SubLedger is a layered billing API for managing plans, customers, subscriptions, invoices, payment attempts, and ledger events.

## Guides

- [Application architecture](architecture.md): domain components, boundaries, and business-rule ownership.
- [API reference](api.md): endpoint contracts, request examples, statuses, and error behavior.
- [Local development](local-development.md): prerequisites, setup, configuration, Docker, and common commands.
- [Testing](testing.md): suite structure, important scenarios, and adding tests.
- [Pipeline architecture](pipelines.md): automated PR checks and manual build/deploy flows.
- [Terraform and AWS deployment](terraform-deployment.md): modules, bootstrapping, GitHub configuration, and cleanup.
- [Security and operations](security-operations.md): secrets, database persistence, reliability, and production follow-up.

The original LLD, ERD, service/repository tables, and core invoice/payment sequences are in the repository [DESIGN.md](../DESIGN.md).
