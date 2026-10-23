import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app import models  # noqa: F401


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def create_customer(client: TestClient, email: str = "alex@example.com") -> dict:
    response = client.post("/customers", json={"email": email, "name": "Alex Doe"})
    assert response.status_code == 201
    return response.json()


def create_plan(client: TestClient, **overrides) -> dict:
    payload = {
        "name": "Standard",
        "price": "49.00",
        "billing_cycle": "monthly",
        "currency": "USD",
    }
    payload.update(overrides)
    response = client.post("/plans", json=payload)
    assert response.status_code == 201
    return response.json()


def create_subscription(client: TestClient, customer_id: int, plan_id: int) -> dict:
    response = client.post("/subscriptions", json={"customer_id": customer_id, "plan_id": plan_id})
    assert response.status_code == 201
    return response.json()