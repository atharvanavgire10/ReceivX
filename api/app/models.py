from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from .db import Base


def utcnow():
    return datetime.now(timezone.utc)


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    industry = Column(String(100))
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "industry": self.industry,
                "created_at": self.created_at.isoformat() if self.created_at else None}


class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(200), nullable=False)
    industry = Column(String(100))
    payment_terms_days = Column(Integer, default=30)
    average_delay_days = Column(Float, default=0)
    reliability_score = Column(Float, default=100)
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id, "company_id": self.company_id, "name": self.name,
            "industry": self.industry, "payment_terms_days": self.payment_terms_days,
            "average_delay_days": self.average_delay_days,
            "reliability_score": self.reliability_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    invoice_number = Column(String(50), nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    issued_at = Column(DateTime, nullable=False)
    due_at = Column(DateTime, nullable=False)
    status = Column(String(20), default="ISSUED")
    risk_score = Column(Float, default=0)
    risk_level = Column(String(20), default="LOW")
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id, "company_id": self.company_id, "buyer_id": self.buyer_id,
            "invoice_number": self.invoice_number, "amount": self.amount,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "status": self.status, "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=utcnow)
    status = Column(String(20), default="COMPLETED")
    reference = Column(String(100))

    def to_dict(self):
        return {
            "id": self.id, "invoice_id": self.invoice_id, "amount": self.amount,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "status": self.status, "reference": self.reference,
        }


class InvoiceEvent(Base):
    __tablename__ = "invoice_events"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    message = Column(Text)
    event_metadata = Column("metadata", JSON)
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id, "invoice_id": self.invoice_id,
            "event_type": self.event_type, "message": self.message,
            "metadata": self.event_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FinancingRequest(Base):
    __tablename__ = "financing_requests"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    status = Column(String(20), default="ELIGIBLE")
    financier = Column(String(100))
    discount_rate = Column(Float)
    settlement_amount = Column(Float)
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id, "invoice_id": self.invoice_id, "status": self.status,
            "financier": self.financier, "discount_rate": self.discount_rate,
            "settlement_amount": self.settlement_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
