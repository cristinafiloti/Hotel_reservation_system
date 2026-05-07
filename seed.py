"""
Seed the application with realistic demo data.
"""
from datetime import date, timedelta
from models import (
    Hotel, SingleRoom, DoubleRoom, Suite,
    SpaService, FoodService, Customer, Admin, Employee
)


def seed_data():
    # ── Hotel ───────────────────────────────────────────────────────────────
    hotel = Hotel(1, "Grand Élysée Hotel", "12 Rue de la Paix, Paris, France", 4.8)

    # ── Rooms ────────────────────────────────────────────────────────────────
    rooms = [
        SingleRoom(1,  "101", 89.0,  "available", ["WiFi", "TV", "Minibar"]),
        SingleRoom(2,  "102", 79.0,  "available", ["WiFi", "TV"]),
        SingleRoom(3,  "103", 95.0,  "available", ["WiFi", "TV", "Sea View"]),
        DoubleRoom(4,  "201", 149.0, "available", ["WiFi", "TV", "Minibar", "Balcony"]),
        DoubleRoom(5,  "202", 139.0, "available", ["WiFi", "TV", "Minibar"]),
        DoubleRoom(6,  "203", 159.0, "reserved",  ["WiFi", "TV", "Jacuzzi"]),
        DoubleRoom(7,  "204", 145.0, "available", ["WiFi", "TV", "City View"]),
        Suite(8,       "301", 349.0, "available", ["WiFi", "TV", "Jacuzzi", "Butler", "Sea View"]),
        Suite(9,       "302", 299.0, "available", ["WiFi", "TV", "Living Room", "Kitchenette"]),
        Suite(10,      "303", 399.0, "reserved",  ["WiFi", "TV", "Private Pool", "Butler"]),
    ]
    hotel.rooms = rooms

    # ── Services ─────────────────────────────────────────────────────────────
    services = [
        SpaService(1,  "Relaxing Massage",    85.0, 60,  "Marie Dubois"),
        SpaService(2,  "Hot Stone Therapy",   110.0, 90, "Jean Moreau"),
        SpaService(3,  "Facial Treatment",    70.0, 45,  "Sophie Laurent"),
        FoodService(4, "Continental Breakfast", 22.0, "Full Continental", 1),
        FoodService(5, "Room Service Dinner",   45.0, "Chef's Menu",      1),
        FoodService(6, "Champagne & Canapés",   85.0, "Premium Package",  1),
    ]
    hotel.services = services

    # ── Users ─────────────────────────────────────────────────────────────────
    admin = Admin(1, "Isabelle Fontaine", "admin@grandelysee.fr", "+33 1 55 00 01", 2)
    employee = Employee(2, "Pierre Martin", "pierre@grandelysee.fr", "+33 1 55 00 02", "Concierge")
    demo_customer = Customer(3, "Alex Johnson", "alex@example.com", "+1 555 0100")

    return {
        "hotel": hotel,
        "rooms": rooms,
        "services": services,
        "admin": admin,
        "employee": employee,
        "demo_customer": demo_customer,
    }
