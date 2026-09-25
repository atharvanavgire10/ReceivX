"""Deterministic risk scoring engine for ReceivX."""


def calculate_risk(invoice, buyer, db):
    """Calculate risk score and reasons for an invoice.
    Returns (score: int 0-100, level: str, reasons: list[str]).
    """
    from .models import Invoice
    score = 0
    reasons = []

    # Factor 1: Buyer historical delay
    if buyer.average_delay_days > 15:
        score += 30
        reasons.append(f"Buyer historically pays {int(buyer.average_delay_days)} days late")
    elif buyer.average_delay_days > 7:
        score += 15
        reasons.append(f"Buyer historically pays {int(buyer.average_delay_days)} days late")
    elif buyer.average_delay_days > 3:
        score += 8
        reasons.append(f"Buyer has minor payment delays ({int(buyer.average_delay_days)} days avg)")

    # Factor 2: Days until due
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if invoice.due_at:
        due = invoice.due_at if invoice.due_at.tzinfo else invoice.due_at.replace(tzinfo=timezone.utc)
        days_remaining = (due - now).days
        if days_remaining < 0:
            score += 25
            reasons.append(f"Invoice is {abs(days_remaining)} days overdue")
        elif days_remaining <= 3:
            score += 15
            reasons.append(f"Invoice is due in {days_remaining} days")
        elif days_remaining <= 7:
            score += 8
            reasons.append(f"Invoice is due in {days_remaining} days")

    # Factor 3: Large invoice amount
    if invoice.amount > 800000:
        score += 15
        reasons.append("Invoice amount is unusually high (>₹8L)")
    elif invoice.amount > 500000:
        score += 8
        reasons.append("Invoice amount is significant (>₹5L)")

    # Factor 4: Buyer reliability
    if buyer.reliability_score < 50:
        score += 20
        reasons.append(f"Buyer reliability is low ({buyer.reliability_score}%)")
    elif buyer.reliability_score < 70:
        score += 10
        reasons.append(f"Buyer reliability is moderate ({buyer.reliability_score}%)")

    # Factor 5: Recent overdue invoices from same buyer
    overdue_count = db.query(Invoice).filter(
        Invoice.buyer_id == buyer.id,
        Invoice.status == "OVERDUE",
        Invoice.id != invoice.id,
    ).count()
    if overdue_count >= 2:
        score += 15
        reasons.append(f"Buyer has {overdue_count} other overdue invoices")
    elif overdue_count == 1:
        score += 8
        reasons.append("Buyer has 1 other overdue invoice")

    score = min(score, 100)

    if score >= 80:
        level = "CRITICAL"
    elif score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level, reasons
