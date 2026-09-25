"""Tests for ReceivX core functionality."""
import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.app.models import Company, Buyer, Invoice, Payment, InvoiceEvent, FinancingRequest
from api.app.rules import calculate_risk


class FakeBuyer:
    def __init__(self, avg_delay=0, reliability=100, id=1):
        self.id = id
        self.average_delay_days = avg_delay
        self.reliability_score = reliability


class FakeInvoice:
    def __init__(self, amount=100000, due_at=None, id=1):
        self.id = id
        self.amount = amount
        self.due_at = due_at


class FakeQuery:
    """Minimal mock for db.query(...).filter(...).count()"""
    def __init__(self, count=0):
        self._count = count

    def __call__(self, *a, **kw):
        return self

    def filter(self, *a, **kw):
        return self

    def count(self):
        return self._count


class FakeDB:
    def __init__(self, overdue_count=0):
        self._overdue_count = overdue_count

    def query(self, *a, **kw):
        return FakeQuery(self._overdue_count)


# --- Risk Engine Tests ---

def test_risk_low_score():
    buyer = FakeBuyer(avg_delay=1, reliability=95)
    from datetime import datetime, timezone, timedelta
    invoice = FakeInvoice(amount=100000, due_at=datetime.now(timezone.utc) + timedelta(days=30))
    score, level, reasons = calculate_risk(invoice, buyer, FakeDB())
    assert score < 30
    assert level == "LOW"


def test_risk_high_delay():
    buyer = FakeBuyer(avg_delay=20, reliability=50)
    from datetime import datetime, timezone, timedelta
    invoice = FakeInvoice(amount=900000, due_at=datetime.now(timezone.utc) + timedelta(days=2))
    score, level, reasons = calculate_risk(invoice, buyer, FakeDB(overdue_count=2))
    assert score >= 60
    assert level in ("HIGH", "CRITICAL")
    assert any("late" in r.lower() for r in reasons)
    assert any("reliability" in r.lower() for r in reasons)


def test_risk_overdue_invoice():
    buyer = FakeBuyer(avg_delay=10, reliability=70)
    from datetime import datetime, timezone, timedelta
    invoice = FakeInvoice(amount=500000, due_at=datetime.now(timezone.utc) - timedelta(days=10))
    score, level, reasons = calculate_risk(invoice, buyer, FakeDB())
    assert score >= 30
    assert any("overdue" in r.lower() for r in reasons)


def test_risk_reasons_not_empty():
    buyer = FakeBuyer(avg_delay=8, reliability=65)
    from datetime import datetime, timezone, timedelta
    invoice = FakeInvoice(amount=600000, due_at=datetime.now(timezone.utc) + timedelta(days=5))
    score, level, reasons = calculate_risk(invoice, buyer, FakeDB())
    assert len(reasons) > 0


def test_risk_score_capped_at_100():
    buyer = FakeBuyer(avg_delay=30, reliability=30)
    from datetime import datetime, timezone, timedelta
    invoice = FakeInvoice(amount=1000000, due_at=datetime.now(timezone.utc) - timedelta(days=30))
    score, level, reasons = calculate_risk(invoice, buyer, FakeDB(overdue_count=5))
    assert score <= 100
    assert level == "CRITICAL"


def test_risk_levels():
    """Verify the level boundaries."""
    buyer_safe = FakeBuyer(avg_delay=0, reliability=100)
    from datetime import datetime, timezone, timedelta
    inv = FakeInvoice(amount=10000, due_at=datetime.now(timezone.utc) + timedelta(days=60))
    score, level, _ = calculate_risk(inv, buyer_safe, FakeDB())
    assert level == "LOW"


# --- Model Tests ---

def test_company_model():
    c = Company(id=1, name="Test Co", industry="Manufacturing")
    d = c.to_dict()
    assert d["name"] == "Test Co"
    assert d["industry"] == "Manufacturing"


def test_invoice_model():
    from datetime import datetime, timezone
    inv = Invoice(
        id=1, company_id=1, buyer_id=1, invoice_number="T-001",
        amount=500000, issued_at=datetime.now(timezone.utc),
        due_at=datetime.now(timezone.utc), status="ISSUED",
        risk_score=0, risk_level="LOW"
    )
    d = inv.to_dict()
    assert d["invoice_number"] == "T-001"
    assert d["amount"] == 500000
    assert d["status"] == "ISSUED"


def test_buyer_model():
    b = Buyer(id=1, company_id=1, name="Test Buyer", industry="Auto",
              payment_terms_days=30, average_delay_days=5, reliability_score=85)
    d = b.to_dict()
    assert d["reliability_score"] == 85
    assert d["payment_terms_days"] == 30
