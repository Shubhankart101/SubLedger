# API Reference

Interactive OpenAPI documentation is served at `/docs`; the raw schema is at `/openapi.json`.

## Routes

| Method | Path | Success response | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health` | `200` | Liveness check |
| `POST` | `/plans` | `201` | Create plan |
| `GET` | `/plans` | `200` | List plans |
| `PUT` | `/plans/{plan_id}` | `200` | Replace plan properties |
| `POST` | `/plans/{plan_id}/deactivate` | `200` | Mark plan inactive |
| `POST` | `/customers` | `201` | Create customer |
| `GET` | `/customers` | `200` | List customers |
| `GET` | `/customers/{customer_id}` | `200` | Fetch customer |
| `GET` | `/customers/{customer_id}/ledger` | `200` | List customer ledger events |
| `POST` | `/subscriptions` | `201` | Create active subscription |
| `GET` | `/subscriptions` | `200` | List subscriptions |
| `PATCH` | `/subscriptions/{subscription_id}/cancel` | `200` | Cancel active subscription |
| `POST` | `/invoices/generate` | `201` | Issue invoice for active subscription |
| `GET` | `/invoices/{invoice_id}` | `200` | Fetch invoice |
| `POST` | `/payments/record` | `201` | Record successful/failed payment attempt |

## Examples

Create a plan:

```json
{
  "name": "Standard",
  "description": "Monthly service",
  "price": "49.00",
  "billing_cycle": "monthly",
  "currency": "USD"
}
```

Generate an invoice; both period dates are optional but must be supplied together:

```json
{
  "subscription_id": 1,
  "period_start": "2026-01-01",
  "period_end": "2026-02-01"
}
```

Record a payment:

```json
{
  "invoice_id": 1,
  "amount": "49.00",
  "currency": "USD",
  "status": "success",
  "provider_reference": "demo-payment-001"
}
```

`status` must be `success` or `failed`. Failed payments can include a `failure_reason`; successful payments must match the invoice currency and cannot exceed the outstanding amount.

## Common Errors

| Status | Meaning |
| --- | --- |
| `404` | Customer, plan, subscription, or invoice does not exist |
| `409` | Duplicate email/plan/period/reference, or invalid lifecycle transition |
| `422` | Invalid request shape or business rule violation |

## Business Invariants

Plan prices and payment amounts must be positive. Customer email and payment provider references are unique. One customer cannot hold two active subscriptions to the same plan. Invoice amount/currency are copied from the plan at issue time. Successful payment updates the invoice to `partially_paid` or `paid`; a failed attempt leaves its balance unchanged. Each invoice and payment event writes a traceable ledger record.
