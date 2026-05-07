"""
Hotel Reservation System – Flask Application
"""
from flask import Flask, render_template, request, jsonify, session
from datetime import date, datetime
from models import (
    Customer, CreditCardPayment, PayPalPayment, BankTransferPayment,
    SpaService, FoodService
)
from seed import seed_data
import json

app = Flask(__name__)
app.secret_key = "hotel-secret-2024"

# ── Global in-memory store (replaces a DB for this demo) ──────────────────────
data = seed_data()
hotel = data["hotel"]
reservations_store = {}   # reservation_id → Reservation
invoices_store = {}       # invoice_id → Invoice
customers_store = {3: data["demo_customer"]}  # id → Customer
_next_customer_id = 10
_next_payment_id = 100
_next_reservation_id = 1


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

def _get_or_create_customer(name: str, email: str, phone: str) -> Customer:
    global _next_customer_id
    for c in customers_store.values():
        if c.email == email:
            return c
    cust = Customer(_next_customer_id, name, email, phone)
    customers_store[_next_customer_id] = cust
    _next_customer_id += 1
    return cust


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", hotel=hotel.to_dict())


@app.route("/rooms")
def rooms_page():
    return render_template("rooms.html", hotel=hotel.to_dict())


@app.route("/reservations")
def reservations_page():
    return render_template("reservations.html")


@app.route("/admin")
def admin_page():
    return render_template("admin.html", hotel=hotel.to_dict())


# ── API: Hotel Info ───────────────────────────────────────────────────────────

@app.route("/api/hotel")
def api_hotel():
    return jsonify(hotel.to_dict())


# ── API: Search Rooms ─────────────────────────────────────────────────────────

@app.route("/api/rooms/search", methods=["POST"])
def api_search_rooms():
    body = request.json or {}
    check_in  = _parse_date(body.get("check_in",  date.today().isoformat()))
    check_out = _parse_date(body.get("check_out", date.today().isoformat()))
    capacity  = int(body.get("capacity", 1))
    max_price = float(body.get("max_price", 9999))
    room_type = body.get("room_type", "all")

    customer = Customer(0, "searcher", "x@x.com", "")
    found = customer.search_available_rooms(hotel, check_in, check_out,
                                            capacity, max_price)
    if room_type != "all":
        found = [r for r in found if r.room_type() == room_type]

    results = []
    for r in found:
        d = r.to_dict()
        d["price_for_stay"] = r.calculate_price(check_in, check_out)
        d["nights"] = (check_out - check_in).days
        results.append(d)

    return jsonify({"rooms": results, "total": len(results)})


# ── API: All Rooms ────────────────────────────────────────────────────────────

@app.route("/api/rooms")
def api_all_rooms():
    return jsonify({"rooms": [r.to_dict() for r in hotel.rooms]})


# ── API: Services ─────────────────────────────────────────────────────────────

@app.route("/api/services")
def api_services():
    return jsonify({"services": [s.to_dict() for s in hotel.services]})


# ── API: Make Reservation ─────────────────────────────────────────────────────

@app.route("/api/reservations", methods=["POST"])
def api_make_reservation():
    global _next_reservation_id
    body = request.json or {}

    # Validate dates
    try:
        check_in  = _parse_date(body["check_in"])
        check_out = _parse_date(body["check_out"])
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid dates"}), 400

    if check_out <= check_in:
        return jsonify({"error": "Check-out must be after check-in"}), 400

    # Find room
    room_id = int(body.get("room_id", 0))
    room = next((r for r in hotel.rooms if r.room_id == room_id), None)
    if not room:
        return jsonify({"error": "Room not found"}), 404
    if room.status != "available":
        return jsonify({"error": "Room is not available"}), 409

    # Customer
    customer = _get_or_create_customer(
        body.get("guest_name", "Guest"),
        body.get("guest_email", "guest@example.com"),
        body.get("guest_phone", ""),
    )

    # Make reservation
    reservation = customer.make_reservation(room, check_in, check_out)
    reservation.reservation_id = _next_reservation_id
    _next_reservation_id += 1

    # Add services
    for svc_id in body.get("service_ids", []):
        svc = next((s for s in hotel.services if s.service_id == int(svc_id)), None)
        if svc:
            reservation.add_service(svc)

    reservations_store[reservation.reservation_id] = reservation
    return jsonify({"success": True, "reservation": reservation.to_dict()}), 201


# ── API: Get Reservation ──────────────────────────────────────────────────────

@app.route("/api/reservations/<int:rid>")
def api_get_reservation(rid):
    res = reservations_store.get(rid)
    if not res:
        return jsonify({"error": "Not found"}), 404
    return jsonify(res.to_dict())


# ── API: Cancel Reservation ───────────────────────────────────────────────────

@app.route("/api/reservations/<int:rid>/cancel", methods=["POST"])
def api_cancel_reservation(rid):
    res = reservations_store.get(rid)
    if not res:
        return jsonify({"error": "Not found"}), 404
    if res.status == "cancelled":
        return jsonify({"error": "Already cancelled"}), 400
    res.cancel_reservation()
    return jsonify({"success": True, "reservation": res.to_dict()})


# ── API: All Reservations ─────────────────────────────────────────────────────

@app.route("/api/reservations")
def api_all_reservations():
    return jsonify({"reservations": [r.to_dict() for r in reservations_store.values()]})


# ── API: Process Payment ──────────────────────────────────────────────────────

@app.route("/api/reservations/<int:rid>/pay", methods=["POST"])
def api_pay(rid):
    global _next_payment_id
    res = reservations_store.get(rid)
    if not res:
        return jsonify({"error": "Reservation not found"}), 404

    body = request.json or {}
    method = body.get("method", "credit_card")
    amount = res.calculate_total_cost()

    if method == "credit_card":
        payment = CreditCardPayment(
            _next_payment_id, amount,
            body.get("card_number", "0000000000000000"),
            body.get("card_holder", "Guest"),
            body.get("expiry", "12/26"),
            body.get("cvv", "123"),
        )
    elif method == "paypal":
        payment = PayPalPayment(_next_payment_id, amount,
                                body.get("paypal_email", "user@paypal.com"))
    else:
        payment = BankTransferPayment(_next_payment_id, amount,
                                      body.get("iban", "DE89370400440532013000"),
                                      body.get("bank_name", "Deutsche Bank"))

    _next_payment_id += 1
    success = payment.process_payment()
    invoice = res.generate_invoice(payment)
    invoices_store[invoice.invoice_id] = invoice

    return jsonify({
        "success": success,
        "payment": payment.to_dict(),
        "invoice": invoice.to_dict(),
    })


# ── API: Admin – Room Stats ───────────────────────────────────────────────────

@app.route("/api/admin/stats")
def api_stats():
    total = len(hotel.rooms)
    available = sum(1 for r in hotel.rooms if r.status == "available")
    reserved  = sum(1 for r in hotel.rooms if r.status == "reserved")
    total_res = len(reservations_store)
    confirmed = sum(1 for r in reservations_store.values() if r.status == "confirmed")
    cancelled = sum(1 for r in reservations_store.values() if r.status == "cancelled")
    revenue   = sum(inv.total_amount for inv in invoices_store.values()
                    if inv.status == "issued")

    return jsonify({
        "rooms": {"total": total, "available": available, "reserved": reserved},
        "reservations": {"total": total_res, "confirmed": confirmed, "cancelled": cancelled},
        "revenue": round(revenue, 2),
        "invoices": len(invoices_store),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
