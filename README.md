# 🏨 Grand Élysée – Hotel Reservation System

A full-stack Python/Flask web application implementing OOP principles (inheritance, polymorphism, encapsulation) for hotel room booking, reservation management, and payment processing.

---

## 📐 Architecture (matches UML diagram)

```
models.py          ← All 10 OOP classes
  User (abstract)
  ├── Customer      inherits User
  ├── Admin         inherits User  
  └── Employee      inherits User
  Room (abstract)   polymorphism
  ├── SingleRoom    — flat nightly rate
  ├── DoubleRoom    — weekend surcharge
  └── Suite         — breakfast credit
  Service (abstract) polymorphism
  ├── SpaService    — per-minute billing
  └── FoodService   — per-item billing
  Payment (abstract) polymorphism
  ├── CreditCardPayment
  ├── PayPalPayment
  └── BankTransferPayment
  Reservation       — orchestrates booking
  Invoice           — auto-generated on payment
  Hotel             — contains rooms & services

app.py             ← Flask routes & REST API
seed.py            ← Demo data
templates/         ← Jinja2 HTML pages
  base.html
  index.html       ← Search & booking page
  rooms.html       ← All rooms + filters
  reservations.html← Guest reservation portal
  admin.html       ← Admin dashboard
```

---

## 🚀 Setup & Run

### 1. Prerequisites
- Python 3.9+
- pip

### 2. Install dependencies
```bash
cd hotel_system
pip install -r requirements.txt
```

### 3. Run the server
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## 🌐 Pages

| URL | Description |
|-----|-------------|
| `/` | Home – search and book rooms |
| `/rooms` | Browse all rooms with filters |
| `/reservations` | Manage/cancel reservations |
| `/admin` | Admin dashboard with KPIs |

## 🔌 REST API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/hotel` | Hotel info |
| POST | `/api/rooms/search` | Search available rooms |
| GET | `/api/rooms` | All rooms |
| GET | `/api/services` | All services |
| POST | `/api/reservations` | Create reservation |
| GET | `/api/reservations` | All reservations |
| GET | `/api/reservations/<id>` | Get reservation |
| POST | `/api/reservations/<id>/cancel` | Cancel |
| POST | `/api/reservations/<id>/pay` | Process payment |
| GET | `/api/admin/stats` | Dashboard stats |

---

## 🎓 OOP Concepts Used

| Concept | Where |
|---------|-------|
| **Inheritance** | Customer, Admin, Employee all extend User |
| **Polymorphism** | Room.calculate_price(), Payment.process_payment(), Service.calculate_cost() |
| **Encapsulation** | Private attributes with `_` prefix and properties |
| **Abstraction** | ABC abstract classes for User, Room, Service, Payment |

---

## 💳 Test Payment Details

**Credit Card:** Any 16-digit number + 3-digit CVV  
**PayPal:** Any valid email address  
**Bank Transfer:** Any IBAN + bank name
