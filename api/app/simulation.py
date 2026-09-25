"""Simulation engine for ReceivX lifecycle actions."""
from datetime import datetime, timezone, timedelta
from .models import Company, Buyer, Invoice, Payment, InvoiceEvent, FinancingRequest
from .rules import calculate_risk
from .db import Base


def utcnow():
    return datetime.now(timezone.utc)


def record_event(db, invoice_id, event_type, message, metadata=None):
    event = InvoiceEvent(
        invoice_id=invoice_id,
        event_type=event_type,
        message=message,
        event_metadata=metadata,
        created_at=utcnow(),
    )
    db.add(event)
    return event


def simulate_payment_delay(db, invoice_id=None):
    """Mark an invoice as payment delayed and overdue, recalculate risk, record events."""
    if invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    else:
        # Pick an active, unpaid, not yet overdue invoice
        invoice = db.query(Invoice).filter(
            Invoice.status.in_(["ISSUED", "ACCEPTED"])
        ).order_by(Invoice.due_at.asc()).first()

    if not invoice:
        return None, "No suitable outstanding invoice found"

    buyer = db.query(Buyer).filter(Buyer.id == invoice.buyer_id).first()
    previous_score = invoice.risk_score

    # Transition to OVERDUE
    invoice.status = "OVERDUE"
    now = utcnow()
    if invoice.due_at:
        due = invoice.due_at if invoice.due_at.tzinfo else invoice.due_at.replace(tzinfo=timezone.utc)
        if due > now:
            invoice.due_at = now - timedelta(days=2)

    # Recalculate risk
    score, level, reasons = calculate_risk(invoice, buyer, db)
    invoice.risk_score = score
    invoice.risk_level = level

    record_event(
        db, invoice.id, "PAYMENT_DELAYED",
        f"Payment expected for invoice {invoice.invoice_number} is delayed past due window",
        {"previous_risk": previous_score, "new_risk": score}
    )
    record_event(
        db, invoice.id, "INVOICE_OVERDUE",
        f"Invoice {invoice.invoice_number} marked OVERDUE (₹{invoice.amount:,.0f})",
        {"status": "OVERDUE"}
    )
    record_event(
        db, invoice.id, "RISK_DETECTED",
        f"Risk escalated to {level} ({score}/100): {'; '.join(reasons[:2])}",
        {"risk_score": score, "risk_level": level, "reasons": reasons}
    )

    db.commit()
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "status": invoice.status,
        "risk_score": invoice.risk_score,
        "risk_level": invoice.risk_level,
        "reasons": reasons,
    }, None


def simulate_payment(db, invoice_id=None):
    """Simulate receiving payment on an invoice, mark settled/paid."""
    if invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    else:
        # Pick an overdue or accepted invoice
        invoice = db.query(Invoice).filter(
            Invoice.status.in_(["OVERDUE", "ACCEPTED", "ISSUED"])
        ).order_by(Invoice.risk_score.desc()).first()

    if not invoice:
        return None, "No outstanding invoice to pay"

    buyer = db.query(Buyer).filter(Buyer.id == invoice.buyer_id).first()

    payment = Payment(
        invoice_id=invoice.id,
        amount=invoice.amount,
        payment_date=utcnow(),
        status="COMPLETED",
        reference=f"RTGS-{int(utcnow().timestamp())}",
    )
    db.add(payment)

    invoice.status = "PAID"
    invoice.risk_score = 0
    invoice.risk_level = "LOW"

    record_event(
        db, invoice.id, "PAYMENT_RECEIVED",
        f"Full payment of ₹{invoice.amount:,.0f} received via RTGS ref {payment.reference}",
        {"amount": invoice.amount, "reference": payment.reference}
    )
    record_event(
        db, invoice.id, "INVOICE_SETTLED",
        f"Invoice {invoice.invoice_number} successfully settled and closed",
        {"status": "PAID"}
    )

    # If there's an active financing request, mark it settled too
    fin = db.query(FinancingRequest).filter(FinancingRequest.invoice_id == invoice.id).first()
    if fin:
        fin.status = "SETTLED"

    db.commit()
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "amount": invoice.amount,
        "status": invoice.status,
        "reference": payment.reference,
    }, None


def simulate_financing(db, invoice_id=None):
    """Simulate financing eligibility, request, and approval flow on an invoice."""
    if invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    else:
        # Find invoice eligible for financing: unpaid, amount >= 200,000, not disputed
        invoice = db.query(Invoice).filter(
            Invoice.status.in_(["ACCEPTED", "OVERDUE", "ISSUED"]),
            Invoice.status != "DISPUTED",
        ).order_by(Invoice.amount.desc()).first()

    if not invoice:
        return None, "No suitable invoice for financing"

    existing_fin = db.query(FinancingRequest).filter(
        FinancingRequest.invoice_id == invoice.id
    ).first()

    discount_rate = 10.4
    settlement_amount = round(invoice.amount * (1 - (discount_rate / 100)), 2)
    financier = "TReDS Platform A (Simulated)"

    if not existing_fin:
        fin = FinancingRequest(
            invoice_id=invoice.id,
            status="APPROVED",
            financier=financier,
            discount_rate=discount_rate,
            settlement_amount=settlement_amount,
            created_at=utcnow(),
        )
        db.add(fin)
    else:
        fin = existing_fin
        fin.status = "APPROVED"
        fin.financier = financier
        fin.discount_rate = discount_rate
        fin.settlement_amount = settlement_amount

    record_event(
        db, invoice.id, "FINANCING_ELIGIBLE",
        f"Invoice {invoice.invoice_number} eligible for TReDS invoice discounting at {discount_rate}%",
        {"financier": financier, "discount_rate": discount_rate, "settlement_amount": settlement_amount}
    )
    record_event(
        db, invoice.id, "FINANCING_REQUESTED",
        f"Financing request submitted to {financier} for ₹{settlement_amount:,.0f}",
        {"financier": financier, "discount_rate": discount_rate}
    )
    record_event(
        db, invoice.id, "FINANCING_APPROVED",
        f"Financing bid approved by {financier}. Early liquidity unlocked: ₹{settlement_amount:,.0f}",
        {"status": "APPROVED", "settlement_amount": settlement_amount}
    )

    db.commit()
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "financing_id": fin.id,
        "financier": fin.financier,
        "discount_rate": fin.discount_rate,
        "settlement_amount": fin.settlement_amount,
        "status": fin.status,
    }, None


def run_full_demo(db):
    """Execute the complete end-to-end recruiter demonstration sequence on real database state."""
    # Find or create a specific demo candidate invoice
    buyer = db.query(Buyer).filter(Buyer.name.ilike("%Tata%")).first()
    if not buyer:
        buyer = db.query(Buyer).first()

    company = db.query(Company).first()
    now = utcnow()

    # Create a fresh target invoice for the demo
    inv_number = f"MPC-DEMO-{int(now.timestamp()) % 10000}"
    invoice = Invoice(
        company_id=company.id if company else 1,
        buyer_id=buyer.id if buyer else 1,
        invoice_number=inv_number,
        amount=850000.0,
        issued_at=now - timedelta(days=28),
        due_at=now + timedelta(days=2),
        status="ACCEPTED",
        risk_score=15,
        risk_level="LOW",
        created_at=now - timedelta(days=28),
    )
    db.add(invoice)
    db.flush()

    record_event(db, invoice.id, "INVOICE_CREATED", f"Demo invoice {inv_number} created for ₹8,50,000")
    record_event(db, invoice.id, "INVOICE_ACCEPTED", f"Invoice accepted by {buyer.name if buyer else 'Buyer'}")
    record_event(db, invoice.id, "INVOICE_DUE_SOON", f"Due date in 2 days — monitoring buyer payment behavior")

    # Step: Delay & Overdue
    invoice.status = "OVERDUE"
    invoice.due_at = now - timedelta(days=3)
    score, level, reasons = calculate_risk(invoice, buyer, db)
    invoice.risk_score = score
    invoice.risk_level = level

    record_event(db, invoice.id, "PAYMENT_DELAYED", f"Payment delay detected beyond normal credit terms")
    record_event(db, invoice.id, "INVOICE_OVERDUE", f"Invoice marked OVERDUE")
    record_event(db, invoice.id, "RISK_DETECTED", f"Risk escalated to {level} ({score}/100): {'; '.join(reasons[:2])}")

    # Step: Financing Flow
    discount_rate = 10.4
    settlement = round(invoice.amount * (1 - (discount_rate / 100)), 2)
    fin = FinancingRequest(
        invoice_id=invoice.id,
        status="APPROVED",
        financier="TReDS Platform A (Simulated)",
        discount_rate=discount_rate,
        settlement_amount=settlement,
        created_at=now,
    )
    db.add(fin)
    record_event(db, invoice.id, "FINANCING_ELIGIBLE", f"Invoice eligible for TReDS factoring at {discount_rate}% APR")
    record_event(db, invoice.id, "FINANCING_REQUESTED", f"Working capital advance requested for ₹{settlement:,.0f}")
    record_event(db, invoice.id, "FINANCING_APPROVED", f"TReDS auction cleared! Liquidity released: ₹{settlement:,.0f}")

    # Step: Payment & Settlement
    pay = Payment(
        invoice_id=invoice.id,
        amount=invoice.amount,
        payment_date=now,
        status="COMPLETED",
        reference=f"TReDS-SETTLE-{invoice.id}",
    )
    db.add(pay)
    invoice.status = "PAID"
    fin.status = "SETTLED"
    record_event(db, invoice.id, "PAYMENT_RECEIVED", f"Institutional settlement received: ₹{invoice.amount:,.0f}")
    record_event(db, invoice.id, "INVOICE_SETTLED", f"Invoice {inv_number} closed with full working capital recovery")

    db.commit()
    return {
        "invoice_id": invoice.id,
        "invoice_number": inv_number,
        "amount": invoice.amount,
        "settlement_amount": settlement,
        "final_status": invoice.status,
    }


def reset_simulation(db):
    """Restore clean demo seed data."""
    from .seed import seed_database
    # Clear all data
    db.query(FinancingRequest).delete()
    db.query(InvoiceEvent).delete()
    db.query(Payment).delete()
    db.query(Invoice).delete()
    db.query(Buyer).delete()
    db.query(Company).delete()
    db.commit()

    # Re-seed
    seed_database(db)
    return {"message": "Demo state reset to initial baseline successfully"}
