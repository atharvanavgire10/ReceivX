"""Core query/service functions for ReceivX."""
from sqlalchemy import func
from .models import Company, Buyer, Invoice, Payment, InvoiceEvent, FinancingRequest


def get_dashboard(db):
    company = db.query(Company).first()
    if not company:
        return {"company": None, "metrics": {}}

    invoices = db.query(Invoice).filter(Invoice.company_id == company.id).all()
    total = len(invoices)
    outstanding = [i for i in invoices if i.status not in ("PAID", "DRAFT")]
    overdue = [i for i in invoices if i.status == "OVERDUE"]
    at_risk = [i for i in outstanding if i.risk_score >= 30]
    financing = db.query(FinancingRequest).join(Invoice).filter(
        Invoice.company_id == company.id,
        FinancingRequest.status.in_(["ELIGIBLE", "REQUESTED"])
    ).count()

    return {
        "company": company.to_dict(),
        "metrics": {
            "total_invoices": total,
            "outstanding_amount": sum(i.amount for i in outstanding),
            "overdue_amount": sum(i.amount for i in overdue),
            "at_risk_amount": sum(i.amount for i in at_risk),
            "at_risk_count": len(at_risk),
            "overdue_count": len(overdue),
            "outstanding_count": len(outstanding),
            "financing_opportunities": financing,
        },
    }


def get_invoices(db):
    rows = db.query(Invoice, Buyer.name.label("buyer_name")).join(
        Buyer, Invoice.buyer_id == Buyer.id
    ).order_by(Invoice.due_at.desc()).all()
    result = []
    for inv, buyer_name in rows:
        d = inv.to_dict()
        d["buyer_name"] = buyer_name
        result.append(d)
    return result


def get_invoice_detail(db, invoice_id):
    inv = db.query(Invoice).get(invoice_id)
    if not inv:
        return None
    buyer = db.query(Buyer).get(inv.buyer_id)
    events = db.query(InvoiceEvent).filter(
        InvoiceEvent.invoice_id == invoice_id
    ).order_by(InvoiceEvent.created_at.desc()).all()
    payments = db.query(Payment).filter(Payment.invoice_id == invoice_id).all()
    financing = db.query(FinancingRequest).filter(
        FinancingRequest.invoice_id == invoice_id
    ).all()
    return {
        "invoice": inv.to_dict(),
        "buyer": buyer.to_dict() if buyer else None,
        "events": [e.to_dict() for e in events],
        "payments": [p.to_dict() for p in payments],
        "financing": [f.to_dict() for f in financing],
    }


def get_buyers(db):
    company = db.query(Company).first()
    if not company:
        return []
    buyers = db.query(Buyer).filter(Buyer.company_id == company.id).order_by(Buyer.name).all()
    result = []
    for b in buyers:
        inv_count = db.query(func.count(Invoice.id)).filter(Invoice.buyer_id == b.id).scalar()
        total_val = db.query(func.coalesce(func.sum(Invoice.amount), 0)).filter(Invoice.buyer_id == b.id).scalar()
        outstanding = db.query(func.count(Invoice.id)).filter(
            Invoice.buyer_id == b.id, Invoice.status.notin_(["PAID", "DRAFT"])
        ).scalar()
        d = b.to_dict()
        d["invoice_count"] = inv_count
        d["total_value"] = float(total_val)
        d["outstanding_count"] = outstanding
        result.append(d)
    return result


def get_buyer_detail(db, buyer_id):
    buyer = db.query(Buyer).get(buyer_id)
    if not buyer:
        return None
    invoices = db.query(Invoice).filter(Invoice.buyer_id == buyer_id).order_by(Invoice.due_at.desc()).all()
    total_val = sum(i.amount for i in invoices)
    outstanding = [i for i in invoices if i.status not in ("PAID", "DRAFT")]
    return {
        "buyer": buyer.to_dict(),
        "invoices": [i.to_dict() for i in invoices],
        "stats": {
            "invoice_count": len(invoices),
            "total_value": total_val,
            "outstanding_count": len(outstanding),
            "outstanding_amount": sum(i.amount for i in outstanding),
        },
    }


def get_events(db, invoice_id=None, limit=50):
    q = db.query(InvoiceEvent)
    if invoice_id:
        q = q.filter(InvoiceEvent.invoice_id == invoice_id)
    return [e.to_dict() for e in q.order_by(InvoiceEvent.created_at.desc()).limit(limit).all()]


def get_financing(db, invoice_id):
    rows = db.query(FinancingRequest).filter(
        FinancingRequest.invoice_id == invoice_id
    ).all()
    return [f.to_dict() for f in rows]
