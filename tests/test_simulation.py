"""Tests for Phase 2: Simulation endpoints, risk engine dynamics, and full demo."""
import sys
import os
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.app.db import Base
from api.app.models import Company, Buyer, Invoice, Payment, InvoiceEvent, FinancingRequest
from api.app.seed import seed_database
from api.app.simulation import (
    simulate_payment_delay,
    simulate_payment,
    simulate_financing,
    run_full_demo,
    reset_simulation,
)
from api.app.services import get_dashboard


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_database(session)
    try:
        yield session
    finally:
        session.close()


def test_simulation_payment_delay(db_session):
    data, err = simulate_payment_delay(db_session)
    assert err is None
    assert data["status"] == "OVERDUE"
    assert data["risk_score"] > 0
    assert len(data["reasons"]) > 0

    # Verify event was recorded
    ev = db_session.query(InvoiceEvent).filter(
        InvoiceEvent.invoice_id == data["invoice_id"],
        InvoiceEvent.event_type == "PAYMENT_DELAYED"
    ).first()
    assert ev is not None


def test_simulation_payment(db_session):
    data, err = simulate_payment(db_session)
    assert err is None
    assert data["status"] == "PAID"
    assert "RTGS-" in data["reference"]

    # Verify payment recorded in db
    payment = db_session.query(Payment).filter(
        Payment.invoice_id == data["invoice_id"]
    ).first()
    assert payment is not None
    assert payment.status == "COMPLETED"


def test_simulation_financing(db_session):
    data, err = simulate_financing(db_session)
    assert err is None
    assert data["status"] == "APPROVED"
    assert data["discount_rate"] > 0
    assert data["settlement_amount"] > 0

    # Verify financing request updated in db
    fin = db_session.query(FinancingRequest).filter(
        FinancingRequest.id == data["financing_id"]
    ).first()
    assert fin is not None
    assert fin.status == "APPROVED"


def test_run_full_demo(db_session):
    init_events_count = db_session.query(InvoiceEvent).count()
    data = run_full_demo(db_session)
    assert data["final_status"] == "PAID"
    assert data["settlement_amount"] > 0

    # Ensure full lifecycle recorded multiple events
    after_events_count = db_session.query(InvoiceEvent).count()
    assert after_events_count > init_events_count

    # Check key lifecycle events exist for this demo invoice
    inv_id = data["invoice_id"]
    types = [
        e.event_type
        for e in db_session.query(InvoiceEvent).filter(InvoiceEvent.invoice_id == inv_id).all()
    ]
    assert "INVOICE_CREATED" in types
    assert "PAYMENT_DELAYED" in types
    assert "RISK_DETECTED" in types
    assert "FINANCING_APPROVED" in types
    assert "INVOICE_SETTLED" in types


def test_reset_simulation(db_session):
    # Alter state
    run_full_demo(db_session)
    res = reset_simulation(db_session)
    assert "reset" in res["message"].lower()

    # Verify clean state re-seeded
    dash = get_dashboard(db_session)
    assert dash["company"]["name"] == "Maharashtra Precision Components"
    assert dash["metrics"]["total_invoices"] == 52
