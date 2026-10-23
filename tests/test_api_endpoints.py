from tests.conftest import create_customer, create_plan, create_subscription


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_plan_list_update_and_deactivate_endpoints(client):
    plan = create_plan(client)
    assert [item["id"] for item in client.get("/plans").json()] == [plan["id"]]

    updated = client.put(
        f"/plans/{plan['id']}",
        json={"name": "Premium", "price": "79.00", "billing_cycle": "yearly", "currency": "USD"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Premium"
    assert updated.json()["price"] == "79.00"

    deactivated = client.post(f"/plans/{plan['id']}/deactivate")
    assert deactivated.status_code == 200
    assert deactivated.json()["status"] == "inactive"
    assert client.put(
        "/plans/9999",
        json={"name": "Missing", "price": "5.00", "billing_cycle": "monthly", "currency": "USD"},
    ).status_code == 404


def test_customer_list_fetch_and_ledger_endpoints(client):
    customer = create_customer(client)
    assert client.get("/customers").json()[0]["id"] == customer["id"]
    assert client.get(f"/customers/{customer['id']}").json()["email"] == customer["email"]
    assert client.get(f"/customers/{customer['id']}/ledger").json() == []
    assert client.get("/customers/9999").status_code == 404
    assert client.get("/customers/9999/ledger").status_code == 404


def test_subscription_list_cancel_and_not_found_endpoints(client):
    customer = create_customer(client)
    plan = create_plan(client)
    subscription = create_subscription(client, customer["id"], plan["id"])
    assert client.get("/subscriptions").json()[0]["id"] == subscription["id"]

    canceled = client.patch(f"/subscriptions/{subscription['id']}/cancel")
    assert canceled.status_code == 200
    assert canceled.json()["status"] == "canceled"
    assert client.patch(f"/subscriptions/{subscription['id']}/cancel").status_code == 409
    assert client.patch("/subscriptions/9999/cancel").status_code == 404


def test_invoice_fetch_missing_and_invalid_generation_endpoints(client):
    customer = create_customer(client)
    plan = create_plan(client)
    subscription = create_subscription(client, customer["id"], plan["id"])
    generated = client.post(
        "/invoices/generate",
        json={
            "subscription_id": subscription["id"],
            "period_start": "2026-01-01",
            "period_end": "2026-02-01",
        },
    )
    assert generated.status_code == 201
    invoice = generated.json()
    assert client.get(f"/invoices/{invoice['id']}").json()["id"] == invoice["id"]
    assert client.get("/invoices/9999").status_code == 404
    assert client.post("/invoices/generate", json={"subscription_id": 9999}).status_code == 404


def test_payment_endpoint_rejects_unknown_invoice(client):
    response = client.post(
        "/payments/record",
        json={
            "invoice_id": 9999,
            "amount": "5.00",
            "currency": "USD",
            "status": "failed",
            "provider_reference": "unknown-invoice-attempt",
        },
    )
    assert response.status_code == 404