"""Flask API routes for ReceivX."""
from flask import Blueprint, jsonify
from .db import get_db
from . import services

api = Blueprint("api", __name__)


def ok(data):
    return jsonify({"success": True, "data": data})


def err(message, status=400):
    return jsonify({"success": False, "error": message}), status


@api.route("/health")
def health():
    try:
        db = next(get_db())
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db.close()
        return ok({"status": "healthy", "database": "connected"})
    except Exception as e:
        return ok({"status": "degraded", "database": str(e)})


@api.route("/dashboard")
def dashboard():
    db = next(get_db())
    try:
        data = services.get_dashboard(db)
        return ok(data)
    finally:
        db.close()


@api.route("/invoices")
def invoices():
    db = next(get_db())
    try:
        return ok(services.get_invoices(db))
    finally:
        db.close()


@api.route("/invoices/<int:invoice_id>")
def invoice_detail(invoice_id):
    db = next(get_db())
    try:
        data = services.get_invoice_detail(db, invoice_id)
        if not data:
            return err("Invoice not found", 404)
        return ok(data)
    finally:
        db.close()


@api.route("/buyers")
def buyers():
    db = next(get_db())
    try:
        return ok(services.get_buyers(db))
    finally:
        db.close()


@api.route("/buyers/<int:buyer_id>")
def buyer_detail(buyer_id):
    db = next(get_db())
    try:
        data = services.get_buyer_detail(db, buyer_id)
        if not data:
            return err("Buyer not found", 404)
        return ok(data)
    finally:
        db.close()


@api.route("/events")
def events():
    db = next(get_db())
    try:
        return ok(services.get_events(db))
    finally:
        db.close()


@api.route("/events/<int:invoice_id>")
def invoice_events(invoice_id):
    db = next(get_db())
    try:
        return ok(services.get_events(db, invoice_id=invoice_id))
    finally:
        db.close()


@api.route("/financing/<int:invoice_id>")
def financing(invoice_id):
    db = next(get_db())
    try:
        return ok(services.get_financing(db, invoice_id))
    finally:
        db.close()


# -------------------------------------------------------------
# Simulation endpoints
# -------------------------------------------------------------
from . import simulation
from flask import request


@api.route("/simulation/run", methods=["POST"])
def sim_run():
    db = next(get_db())
    try:
        data = simulation.run_full_demo(db)
        return ok(data)
    finally:
        db.close()


@api.route("/simulation/payment-delay", methods=["POST"])
def sim_payment_delay():
    db = next(get_db())
    try:
        payload = request.get_json(silent=True) or {}
        inv_id = payload.get("invoice_id")
        data, error = simulation.simulate_payment_delay(db, invoice_id=inv_id)
        if error:
            return err(error, 400)
        return ok(data)
    finally:
        db.close()


@api.route("/simulation/payment", methods=["POST"])
def sim_payment():
    db = next(get_db())
    try:
        payload = request.get_json(silent=True) or {}
        inv_id = payload.get("invoice_id")
        data, error = simulation.simulate_payment(db, invoice_id=inv_id)
        if error:
            return err(error, 400)
        return ok(data)
    finally:
        db.close()


@api.route("/simulation/financing", methods=["POST"])
def sim_financing():
    db = next(get_db())
    try:
        payload = request.get_json(silent=True) or {}
        inv_id = payload.get("invoice_id")
        data, error = simulation.simulate_financing(db, invoice_id=inv_id)
        if error:
            return err(error, 400)
        return ok(data)
    finally:
        db.close()


@api.route("/simulation/reset", methods=["POST"])
def sim_reset():
    db = next(get_db())
    try:
        data = simulation.reset_simulation(db)
        return ok(data)
    finally:
        db.close()

