from tests.conftest import create_customer, create_plan, create_subscription


def test_plan_price_must_be_positive(client):
    response = client.post(
        "/plans",
        json={"name": "Free", "price": "0", "billing_cycle": "monthly", "currency": "USD"},
    )
    assert response.status_code == 422


def test_customer_email_must_be_unique(client):
    create_customer(client)
    response = client.post("/customers", json={"email": "alex@example.com", "name": "Alex Again"})
    assert response.status_code == 409


def test_inactive_plan_cannot_be_subscribed_to(client):
    customer = create_customer(client)
    plan = create_plan(client)
    assert client.post(f"/plans/{plan['id']}/deactivate").status_code == 200
    response = client.post(
        "/subscriptions", json={"customer_id": customer["id"], "plan_id": plan["id"]}
    )
    assert response.status_code == 422


def test_customer_cannot_have_duplicate_active_plan_subscription(client):
    customer = create_customer(client)
    plan = create_plan(client)
    create_subscription(client, customer["id"], plan["id"])
    response = client.post(
        "/subscriptions", json={"customer_id": customer["id"], "plan_id": plan["id"]}
    )
    assert response.status_code == 409


def test_invoice_snapshots_plan_price_and_writes_ledger(client):
    customer = create_customer(client)
    plan = create_plan(client, price="49.00")
    subscription = create_subscription(client, customer["id"], plan["id"])
    invoice_response = client.post("/invoices/generate", json={"subscription_id": subscription["id"]})
    assert invoice_response.status_code == 201
    invoice = invoice_response.json()
    assert invoice["amount_due"] == "49.00"

    client.put(
        f"/plans/{plan['id']}",
        json={"name": "Standard", "price": "59.00", "billing_cycle": "monthly", "currency": "USD"},
    )
    assert client.get(f"/invoices/{invoice['id']}").json()["amount_due"] == "49.00"
    ledger = client.get(f"/customers/{customer['id']}/ledger").json()
    assert [entry["entry_type"] for entry in ledger] == ["invoice_created"]


def test_failed_payment_does_not_increase_amount_paid(client):
    customer = create_customer(client)
    plan = create_plan(client)
    subscription = create_subscription(client, customer["id"], plan["id"])
    invoice = client.post("/invoices/generate", json={"subscription_id": subscription["id"]}).json()
    response = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "20.00",
            "currency": "USD",
            "status": "failed",
            "provider_reference": "pay-failed-1",
            "failure_reason": "Insufficient funds",
        },
    )
    assert response.status_code == 201
    assert response.json()["invoice"]["amount_paid"] == "0.00"
    ledger = client.get(f"/customers/{customer['id']}/ledger").json()
    assert ledger[-1]["entry_type"] == "payment_failure"


def test_successful_payment_cannot_exceed_balance_and_marks_paid(client):
    customer = create_customer(client)
    plan = create_plan(client)
    subscription = create_subscription(client, customer["id"], plan["id"])
    invoice = client.post("/invoices/generate", json={"subscription_id": subscription["id"]}).json()

    too_large = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "50.00",
            "currency": "USD",
            "status": "success",
            "provider_reference": "pay-too-large",
        },
    )
    assert too_large.status_code == 422

    partial = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "19.00",
            "currency": "USD",
            "status": "success",
            "provider_reference": "pay-partial",
        },
    )
    assert partial.json()["invoice"]["status"] == "partially_paid"

    final = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "30.00",
            "currency": "USD",
            "status": "success",
            "provider_reference": "pay-final",
        },
    )
    assert final.json()["invoice"]["status"] == "paid"
    assert final.json()["invoice"]["amount_paid"] == "49.00"


def test_canceled_subscription_can_be_recreated(client):
    customer = create_customer(client)
    plan = create_plan(client)
    subscription = create_subscription(client, customer["id"], plan["id"])
    assert client.patch(f"/subscriptions/{subscription['id']}/cancel").status_code == 200
    recreated = client.post(
        "/subscriptions", json={"customer_id": customer["id"], "plan_id": plan["id"]}
    )
    assert recreated.status_code == 201
    assert client.patch(f"/subscriptions/{recreated.json()['id']}/cancel").status_code == 200
    assert client.post(
        "/subscriptions", json={"customer_id": customer["id"], "plan_id": plan["id"]}
    ).status_code == 201


def test_successful_payment_must_match_invoice_currency(client):
    customer = create_customer(client)
    plan = create_plan(client)
    subscription = create_subscription(client, customer["id"], plan["id"])
    invoice = client.post("/invoices/generate", json={"subscription_id": subscription["id"]}).json()
    response = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "10.00",
            "currency": "EUR",
            "status": "success",
            "provider_reference": "currency-mismatch",
        },
    )
    assert response.status_code == 422


def test_invoice_rejects_duplicate_period(client):
    customer = create_customer(client)
    plan = create_plan(client)
    subscription = create_subscription(client, customer["id"], plan["id"])
    payload = {
        "subscription_id": subscription["id"],
        "period_start": "2026-01-01",
        "period_end": "2026-02-01",
    }
    assert client.post("/invoices/generate", json=payload).status_code == 201
    assert client.post("/invoices/generate", json=payload).status_code == 409