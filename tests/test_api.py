"""End-to-end API integration tests verifying health, error handling, responses, and flows."""
import sys
import os
import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.app.db import Base, SessionLocal
from api.app.seed import seed_database
from api.index import app


@pytest.fixture
def client():
    # Setup test in-memory database and patch SessionLocal
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    seed_database(session)

    # Patch get_db to return testing session
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    import api.app.routes
    import api.app.db
    api.app.routes.get_db = override_get_db
    api.app.db.get_db = override_get_db

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

    session.close()


def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "status" in data["data"]


def test_api_dashboard(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["company"]["name"] == "Maharashtra Precision Components"
    assert data["data"]["metrics"]["total_invoices"] >= 50
    assert data["data"]["metrics"]["outstanding_amount"] > 0


def test_api_invoices_list(client):
    res = client.get("/api/invoices")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["data"]) >= 50
    assert "invoice_number" in data["data"][0]


def test_api_invoice_detail_valid_and_invalid(client):
    # Valid
    res = client.get("/api/invoices/1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "invoice" in data["data"]
    assert "buyer" in data["data"]
    assert "events" in data["data"]

    # Invalid ID returns 404
    res_invalid = client.get("/api/invoices/999999")
    assert res_invalid.status_code == 404
    inv_data = res_invalid.get_json()
    assert inv_data["success"] is False
    assert "not found" in inv_data["error"].lower()


def test_api_simulation_flow(client):
    # 1. Trigger delay
    res_delay = client.post("/api/simulation/payment-delay")
    assert res_delay.status_code == 200
    d_data = res_delay.get_json()
    assert d_data["success"] is True
    assert d_data["data"]["status"] == "OVERDUE"

    # 2. Trigger financing
    res_fin = client.post("/api/simulation/financing")
    assert res_fin.status_code == 200
    f_data = res_fin.get_json()
    assert f_data["success"] is True
    assert f_data["data"]["status"] == "APPROVED"

    # 3. Trigger payment
    res_pay = client.post("/api/simulation/payment")
    assert res_pay.status_code == 200
    p_data = res_pay.get_json()
    assert p_data["success"] is True
    assert p_data["data"]["status"] == "PAID"

    # 4. Trigger reset
    res_reset = client.post("/api/simulation/reset")
    assert res_reset.status_code == 200
    r_data = res_reset.get_json()
    assert r_data["success"] is True
