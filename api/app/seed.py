"""Seed database with realistic synthetic MSME data."""
from datetime import datetime, timezone, timedelta
from .models import Company, Buyer, Invoice, Payment, InvoiceEvent, FinancingRequest
from .db import Base

BUYERS_DATA = [
    {"name": "Tata Motors Ltd", "industry": "Automotive", "payment_terms_days": 45, "average_delay_days": 3, "reliability_score": 92},
    {"name": "Bajaj Auto Ltd", "industry": "Automotive", "payment_terms_days": 30, "average_delay_days": 5, "reliability_score": 88},
    {"name": "Mahindra & Mahindra", "industry": "Automotive", "payment_terms_days": 60, "average_delay_days": 12, "reliability_score": 72},
    {"name": "Godrej Industries", "industry": "Manufacturing", "payment_terms_days": 30, "average_delay_days": 2, "reliability_score": 95},
    {"name": "Larsen & Toubro", "industry": "Engineering", "payment_terms_days": 45, "average_delay_days": 8, "reliability_score": 80},
    {"name": "Thermax Ltd", "industry": "Energy", "payment_terms_days": 30, "average_delay_days": 18, "reliability_score": 55},
    {"name": "Bharat Forge", "industry": "Automotive", "payment_terms_days": 45, "average_delay_days": 15, "reliability_score": 62},
    {"name": "Kirloskar Oil Engines", "industry": "Manufacturing", "payment_terms_days": 30, "average_delay_days": 6, "reliability_score": 85},
    {"name": "Cummins India", "industry": "Engineering", "payment_terms_days": 45, "average_delay_days": 4, "reliability_score": 90},
    {"name": "Siemens India", "industry": "Engineering", "payment_terms_days": 60, "average_delay_days": 20, "reliability_score": 48},
    {"name": "Ashok Leyland", "industry": "Automotive", "payment_terms_days": 30, "average_delay_days": 10, "reliability_score": 75},
    {"name": "Bosch India", "industry": "Automotive", "payment_terms_days": 45, "average_delay_days": 1, "reliability_score": 97},
]


def seed_database(db):
    """Create demo company, buyers, invoices, payments, and events."""
    # Check if already seeded
    if db.query(Company).first():
        return False

    now = datetime.now(timezone.utc)

    # Company
    company = Company(name="Maharashtra Precision Components", industry="Precision Manufacturing")
    db.add(company)
    db.flush()

    # Buyers
    buyers = []
    for bd in BUYERS_DATA:
        b = Buyer(company_id=company.id, **bd)
        db.add(b)
        buyers.append(b)
    db.flush()

    invoice_num = 1000

    # Generate invoices with varied statuses
    invoices_spec = []

    # PAID invoices (historical) — 20
    for i in range(20):
        buyer = buyers[i % len(buyers)]
        days_ago = 90 + i * 5
        amount = 150000 + (i * 37000) % 700000
        invoices_spec.append({
            "buyer": buyer, "amount": amount, "status": "PAID",
            "issued_days_ago": days_ago, "due_days_ago": days_ago - buyer.payment_terms_days,
            "risk_score": 0, "risk_level": "LOW",
        })

    # ISSUED / ACCEPTED (outstanding, low risk) — 10
    for i in range(10):
        buyer = buyers[i % 5]  # reliable buyers
        amount = 200000 + (i * 50000) % 600000
        invoices_spec.append({
            "buyer": buyer, "amount": amount, "status": "ACCEPTED" if i % 2 == 0 else "ISSUED",
            "issued_days_ago": 15 + i * 3, "due_days_from_now": 10 + i * 5,
            "risk_score": 5 + i * 2, "risk_level": "LOW",
        })

    # DUE SOON (medium risk) — 8
    for i in range(8):
        buyer = buyers[4 + i % 4]
        amount = 300000 + (i * 80000) % 500000
        invoices_spec.append({
            "buyer": buyer, "amount": amount, "status": "ACCEPTED",
            "issued_days_ago": 25 + i * 2, "due_days_from_now": 1 + i,
            "risk_score": 35 + i * 3, "risk_level": "MEDIUM",
        })

    # OVERDUE (high risk) — 8
    for i in range(8):
        buyer = buyers[5 + i % 4]  # less reliable buyers
        amount = 400000 + (i * 100000) % 600000
        invoices_spec.append({
            "buyer": buyer, "amount": amount, "status": "OVERDUE",
            "issued_days_ago": 50 + i * 5, "due_days_ago": 5 + i * 3,
            "risk_score": 65 + i * 4, "risk_level": "HIGH" if 65 + i * 4 < 80 else "CRITICAL",
        })

    # DISPUTED — 2
    for i in range(2):
        buyer = buyers[9 + i]
        invoices_spec.append({
            "buyer": buyer, "amount": 750000 + i * 100000, "status": "DISPUTED",
            "issued_days_ago": 40 + i * 10, "due_days_ago": 10 + i * 5,
            "risk_score": 85 + i * 5, "risk_level": "CRITICAL",
        })

    # Financing-eligible — 4 (accepted, unpaid, good amount)
    for i in range(4):
        buyer = buyers[i % 3]
        invoices_spec.append({
            "buyer": buyer, "amount": 600000 + i * 150000, "status": "ACCEPTED",
            "issued_days_ago": 20 + i * 3, "due_days_from_now": 15 + i * 5,
            "risk_score": 10 + i * 5, "risk_level": "LOW",
            "financing_eligible": True,
        })

    # Create all invoices
    for spec in invoices_spec:
        invoice_num += 1
        buyer = spec["buyer"]
        issued_at = now - timedelta(days=spec["issued_days_ago"])

        if "due_days_from_now" in spec:
            due_at = now + timedelta(days=spec["due_days_from_now"])
        else:
            due_at = now - timedelta(days=spec.get("due_days_ago", 0))

        inv = Invoice(
            company_id=company.id, buyer_id=buyer.id,
            invoice_number=f"MPC-{invoice_num}",
            amount=spec["amount"], issued_at=issued_at, due_at=due_at,
            status=spec["status"], risk_score=spec["risk_score"],
            risk_level=spec["risk_level"],
        )
        db.add(inv)
        db.flush()

        # Events
        db.add(InvoiceEvent(
            invoice_id=inv.id, event_type="INVOICE_CREATED",
            message=f"Invoice {inv.invoice_number} created for ₹{inv.amount:,.0f}",
        ))

        if spec["status"] != "DRAFT":
            db.add(InvoiceEvent(
                invoice_id=inv.id, event_type="INVOICE_ACCEPTED",
                message=f"Invoice {inv.invoice_number} accepted by {buyer.name}",
            ))

        if spec["status"] == "PAID":
            pay_date = due_at + timedelta(days=int(buyer.average_delay_days))
            db.add(Payment(
                invoice_id=inv.id, amount=inv.amount,
                payment_date=pay_date, status="COMPLETED",
                reference=f"PAY-{inv.id}-{buyer.id}",
            ))
            db.add(InvoiceEvent(
                invoice_id=inv.id, event_type="PAYMENT_RECEIVED",
                message=f"Payment of ₹{inv.amount:,.0f} received",
            ))

        if spec["status"] == "OVERDUE":
            db.add(InvoiceEvent(
                invoice_id=inv.id, event_type="INVOICE_OVERDUE",
                message=f"Invoice {inv.invoice_number} is overdue",
            ))
            db.add(InvoiceEvent(
                invoice_id=inv.id, event_type="RISK_DETECTED",
                message=f"Risk score: {spec['risk_score']} ({spec['risk_level']})",
            ))

        if spec.get("financing_eligible"):
            db.add(FinancingRequest(
                invoice_id=inv.id, status="ELIGIBLE",
                financier="TReDS Platform A", discount_rate=10.4,
                settlement_amount=round(inv.amount * 0.896, 2),
            ))

    db.commit()
    return True
