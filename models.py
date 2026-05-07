"""
Hotel Reservation System - Core OOP Models
Implements inheritance, polymorphism, and encapsulation as per UML diagram.
"""

from datetime import date, datetime
from abc import ABC, abstractmethod
from typing import List, Optional
import uuid


# ─────────────────────────────────────────────
#  USER HIERARCHY  (Inheritance)
# ─────────────────────────────────────────────

class User(ABC):
    """Base class – all actors in the system inherit from here."""

    def __init__(self, user_id: int, name: str, email: str, phone: str):
        self._id = user_id
        self._name = name
        self._email = email
        self._phone = phone

    @property
    def id(self): return self._id
    @property
    def name(self): return self._name
    @property
    def email(self): return self._email
    @property
    def phone(self): return self._phone

    def to_dict(self):
        return {"id": self._id, "name": self._name,
                "email": self._email, "phone": self._phone,
                "role": self.__class__.__name__}


class Customer(User):
    """End-user who searches and books rooms."""

    def __init__(self, user_id: int, name: str, email: str, phone: str):
        super().__init__(user_id, name, email, phone)
        self._reservations: List["Reservation"] = []

    def search_available_rooms(self, hotel: "Hotel", check_in: date,
                               check_out: date, capacity: int = 1,
                               max_price: float = 9999) -> List["Room"]:
        return [r for r in hotel.rooms
                if r.status == "available"
                and r.capacity >= capacity
                and r.base_price <= max_price]

    def make_reservation(self, room: "Room", check_in: date,
                         check_out: date) -> "Reservation":
        res = Reservation(
            reservation_id=len(self._reservations) + 1,
            customer=self,
            room=room,
            check_in=check_in,
            check_out=check_out,
        )
        self._reservations.append(res)
        room.status = "reserved"
        return res

    def cancel_reservation(self, reservation_id: int) -> bool:
        for res in self._reservations:
            if res.reservation_id == reservation_id:
                res.cancel_reservation()
                return True
        return False

    @property
    def reservations(self): return self._reservations


class Admin(User):
    """System administrator with elevated privileges."""

    def __init__(self, user_id: int, name: str, email: str,
                 phone: str, admin_level: int = 1):
        super().__init__(user_id, name, email, phone)
        self.admin_level = admin_level

    def manage_rooms(self, hotel: "Hotel", room: "Room", action: str):
        if action == "add":
            hotel.rooms.append(room)
        elif action == "remove":
            hotel.rooms = [r for r in hotel.rooms if r.room_id != room.room_id]

    def manage_services(self, hotel: "Hotel", service: "Service", action: str):
        if action == "add":
            hotel.services.append(service)
        elif action == "remove":
            hotel.services = [s for s in hotel.services
                              if s.service_id != service.service_id]

    def manage_reservations(self, reservations: List["Reservation"]):
        return reservations


class Employee(User):
    """Hotel staff member."""

    def __init__(self, user_id: int, name: str, email: str,
                 phone: str, role: str):
        super().__init__(user_id, name, email, phone)
        self.role = role

    def manage_reservations(self, reservations: List["Reservation"]):
        return [r for r in reservations if r.status == "confirmed"]

    def manage_rooms(self, hotel: "Hotel"):
        return hotel.rooms


# ─────────────────────────────────────────────
#  ROOM HIERARCHY  (Polymorphism)
# ─────────────────────────────────────────────

class Room(ABC):
    """Abstract base room – subclasses override price logic."""

    PRICE_MULTIPLIERS = {"SingleRoom": 1.0, "DoubleRoom": 1.6, "Suite": 3.2}

    def __init__(self, room_id: int, number: str, base_price: float,
                 capacity: int, status: str = "available", amenities: list = None):
        self._room_id = room_id
        self._number = number
        self._base_price = base_price
        self._capacity = capacity
        self._status = status
        self._amenities = amenities or []

    @property
    def room_id(self): return self._room_id
    @property
    def number(self): return self._number
    @property
    def base_price(self): return self._base_price
    @property
    def capacity(self): return self._capacity
    @property
    def status(self): return self._status
    @status.setter
    def status(self, value): self._status = value
    @property
    def amenities(self): return self._amenities

    @abstractmethod
    def calculate_price(self, check_in: date, check_out: date) -> float:
        """Polymorphic price calculation."""

    def _nights(self, check_in: date, check_out: date) -> int:
        return max(1, (check_out - check_in).days)

    def room_type(self) -> str:
        return self.__class__.__name__

    def to_dict(self):
        return {
            "room_id": self._room_id, "number": self._number,
            "base_price": self._base_price, "capacity": self._capacity,
            "status": self._status, "room_type": self.room_type(),
            "amenities": self._amenities,
        }


class SingleRoom(Room):
    """1 guest – standard nightly rate."""

    def __init__(self, room_id, number, base_price, status="available", amenities=None):
        super().__init__(room_id, number, base_price, capacity=1,
                         status=status, amenities=amenities)

    def calculate_price(self, check_in: date, check_out: date) -> float:
        return self._nights(check_in, check_out) * self._base_price


class DoubleRoom(Room):
    """2 guests – 10 % weekend surcharge."""

    def __init__(self, room_id, number, base_price, status="available", amenities=None):
        super().__init__(room_id, number, base_price, capacity=2,
                         status=status, amenities=amenities)

    def calculate_price(self, check_in: date, check_out: date) -> float:
        nights = self._nights(check_in, check_out)
        total = 0.0
        for i in range(nights):
            from datetime import timedelta
            day = check_in + timedelta(days=i)
            surcharge = 1.10 if day.weekday() >= 5 else 1.0
            total += self._base_price * surcharge
        return round(total, 2)


class Suite(Room):
    """4 guests – luxury rate with complimentary breakfast credit."""

    BREAKFAST_CREDIT = 40.0

    def __init__(self, room_id, number, base_price, status="available", amenities=None):
        super().__init__(room_id, number, base_price, capacity=4,
                         status=status, amenities=amenities)

    def calculate_price(self, check_in: date, check_out: date) -> float:
        nights = self._nights(check_in, check_out)
        return round(nights * self._base_price - self.BREAKFAST_CREDIT, 2)


# ─────────────────────────────────────────────
#  SERVICE HIERARCHY  (Polymorphism)
# ─────────────────────────────────────────────

class Service(ABC):
    """Abstract service – subclasses implement cost logic."""

    def __init__(self, service_id: int, name: str, price: float):
        self._service_id = service_id
        self._name = name
        self._price = price

    @property
    def service_id(self): return self._service_id
    @property
    def name(self): return self._name
    @property
    def price(self): return self._price

    @abstractmethod
    def calculate_cost(self) -> float:
        """Each service calculates differently."""

    def to_dict(self):
        return {"service_id": self._service_id, "name": self._name,
                "price": self._price, "type": self.__class__.__name__,
                "cost": self.calculate_cost()}


class SpaService(Service):
    """Per-minute billing with therapist premium."""

    THERAPIST_PREMIUM = 25.0

    def __init__(self, service_id, name, price, duration: int,
                 therapist_name: str):
        super().__init__(service_id, name, price)
        self.duration = duration          # minutes
        self.therapist_name = therapist_name

    def calculate_cost(self) -> float:
        return round(self._price * (self.duration / 60) + self.THERAPIST_PREMIUM, 2)

    def to_dict(self):
        d = super().to_dict()
        d.update({"duration": self.duration, "therapist": self.therapist_name})
        return d


class FoodService(Service):
    """Per-item billing."""

    def __init__(self, service_id, name, price, menu_item: str, quantity: int):
        super().__init__(service_id, name, price)
        self.menu_item = menu_item
        self.quantity = quantity

    def calculate_cost(self) -> float:
        return round(self._price * self.quantity, 2)

    def to_dict(self):
        d = super().to_dict()
        d.update({"menu_item": self.menu_item, "quantity": self.quantity})
        return d


# ─────────────────────────────────────────────
#  PAYMENT HIERARCHY  (Polymorphism)
# ─────────────────────────────────────────────

class Payment(ABC):
    """Abstract payment – subclasses implement processing logic."""

    def __init__(self, payment_id: int, amount: float):
        self._payment_id = payment_id
        self._amount = amount
        self._payment_date: Optional[date] = None
        self._status = "pending"

    @property
    def payment_id(self): return self._payment_id
    @property
    def amount(self): return self._amount
    @property
    def status(self): return self._status

    @abstractmethod
    def process_payment(self) -> bool:
        """Each payment method has unique validation logic."""

    def to_dict(self):
        return {
            "payment_id": self._payment_id, "amount": self._amount,
            "status": self._status,
            "date": self._payment_date.isoformat() if self._payment_date else None,
            "type": self.__class__.__name__,
        }


class CreditCardPayment(Payment):
    """Validates card format before processing."""

    def __init__(self, payment_id, amount, card_number: str,
                 card_holder: str, expiry: str, cvv: str):
        super().__init__(payment_id, amount)
        self._card_masked = "**** **** **** " + card_number[-4:]
        self._card_holder = card_holder
        self._expiry = expiry
        self._cvv = cvv

    def process_payment(self) -> bool:
        # Simulate validation
        if len(self._cvv) in (3, 4) and self._expiry:
            self._status = "completed"
            self._payment_date = date.today()
            return True
        self._status = "failed"
        return False

    def to_dict(self):
        d = super().to_dict()
        d.update({"card_masked": self._card_masked, "holder": self._card_holder})
        return d


class PayPalPayment(Payment):
    """Validates PayPal email before processing."""

    def __init__(self, payment_id, amount, paypal_email: str):
        super().__init__(payment_id, amount)
        self._paypal_email = paypal_email

    def process_payment(self) -> bool:
        if "@" in self._paypal_email:
            self._status = "completed"
            self._payment_date = date.today()
            return True
        self._status = "failed"
        return False

    def to_dict(self):
        d = super().to_dict()
        d["paypal_email"] = self._paypal_email
        return d


class BankTransferPayment(Payment):
    """Direct bank transfer – always succeeds (cleared offline)."""

    def __init__(self, payment_id, amount, iban: str, bank_name: str):
        super().__init__(payment_id, amount)
        self._iban = iban
        self._bank_name = bank_name

    def process_payment(self) -> bool:
        self._status = "pending_clearance"
        self._payment_date = date.today()
        return True

    def to_dict(self):
        d = super().to_dict()
        d.update({"iban": self._iban[-4:], "bank": self._bank_name})
        return d


# ─────────────────────────────────────────────
#  INVOICE
# ─────────────────────────────────────────────

class Invoice:
    _counter = 1

    def __init__(self, reservation: "Reservation", payment: Payment):
        self.invoice_id = Invoice._counter
        Invoice._counter += 1
        self.issue_date = date.today()
        self.reservation = reservation
        self.payment = payment
        self.total_amount = reservation.calculate_total_cost()
        self.status = "issued" if payment.status == "completed" else "unpaid"

    def to_dict(self):
        return {
            "invoice_id": self.invoice_id,
            "issue_date": self.issue_date.isoformat(),
            "total_amount": self.total_amount,
            "status": self.status,
            "payment": self.payment.to_dict(),
            "reservation": self.reservation.to_dict(),
        }


# ─────────────────────────────────────────────
#  RESERVATION
# ─────────────────────────────────────────────

class Reservation:
    def __init__(self, reservation_id: int, customer: Customer,
                 room: Room, check_in: date, check_out: date):
        self.reservation_id = reservation_id
        self.customer = customer
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.status = "confirmed"
        self.services: List[Service] = []
        self._invoice: Optional[Invoice] = None

    def add_service(self, service: Service):
        self.services.append(service)

    def calculate_total_cost(self) -> float:
        room_cost = self.room.calculate_price(self.check_in, self.check_out)
        service_cost = sum(s.calculate_cost() for s in self.services)
        return round(room_cost + service_cost, 2)

    def generate_invoice(self, payment: Payment) -> Invoice:
        inv = Invoice(self, payment)
        self._invoice = inv
        return inv

    def cancel_reservation(self):
        self.status = "cancelled"
        self.room.status = "available"

    def to_dict(self):
        return {
            "reservation_id": self.reservation_id,
            "customer": self.customer.name,
            "room": self.room.to_dict(),
            "check_in": self.check_in.isoformat(),
            "check_out": self.check_out.isoformat(),
            "nights": (self.check_out - self.check_in).days,
            "status": self.status,
            "services": [s.to_dict() for s in self.services],
            "total_cost": self.calculate_total_cost(),
        }


# ─────────────────────────────────────────────
#  HOTEL
# ─────────────────────────────────────────────

class Hotel:
    def __init__(self, hotel_id: int, name: str, address: str, rating: float):
        self.hotel_id = hotel_id
        self.name = name
        self.address = address
        self.rating = rating
        self.rooms: List[Room] = []
        self.services: List[Service] = []

    def to_dict(self):
        return {
            "hotel_id": self.hotel_id, "name": self.name,
            "address": self.address, "rating": self.rating,
            "total_rooms": len(self.rooms),
            "available_rooms": sum(1 for r in self.rooms if r.status == "available"),
        }
