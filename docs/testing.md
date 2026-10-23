# Testing

## Run the Suite

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

Tests use FastAPI `TestClient` and a fresh in-memory SQLite database per test. They do not contact payment providers, AWS, or an external database.

## Coverage Intent

- `tests/test_billing_rules.py` verifies plan pricing, unique customer email, inactive plan rejection, active subscription uniqueness and lifecycle, invoice price snapshots and duplicate periods, payment currency and balance rules, failed-payment balance behavior, payment ledger records, and full/partial settlement.
- `tests/test_api_endpoints.py` exercises health, plan listing/updating/deactivation, customer list/fetch/ledger, subscription listing/cancellation, invoice generation/fetch, and payment error responses.
- Shared client and domain-object helpers are in `tests/conftest.py`.

When adding an endpoint, cover a normal response, its expected error response, and side effects on related entities or the ledger when relevant. Keep fixtures isolated so endpoint tests are order-independent.
