<div align="center">

# 🏭 Multi-Stock Logistics Platform

### Enterprise-Grade Warehouse & Logistics Management System

[![Django](https://img.shields.io/badge/Django-4.2.11-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Frontend%20Live%20on%20Vercel-brightgreen?style=for-the-badge)](https://vercel.com)

**[🌐 Frontend Demo (Vercel)](https://vercel.com)** &nbsp;•&nbsp; **[🐛 Report Bug](https://github.com/AshishCherian15/Multi-Stock-Logistics-Platform/issues)** &nbsp;•&nbsp; **[💡 Request Feature](https://github.com/AshishCherian15/Multi-Stock-Logistics-Platform/issues)**

---

> *Final Year B.E. Computer Science & Engineering Project — 2025–26 | USN: 4KM22CS018*

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Screenshots](#-screenshots)
- [Local Setup](#-local-setup)
- [Project Structure](#-project-structure)
- [Role-Based Access](#-role-based-access)
- [Deployment](#-deployment-github--vercel-frontend)
- [API Reference](#-api-reference)
- [Author](#-author)

---

## 🧠 About

**Multi-Stock Logistics Platform** is a comprehensive, production-ready warehouse and logistics management system built with Django and PostgreSQL. It covers the full lifecycle of a logistics business — from inventory tracking and multi-vendor marketplace to equipment rentals, smart locker bookings, POS billing, analytics dashboards, and customer support.

Built as a Final Year CS Engineering project, it demonstrates enterprise software engineering patterns: role-based access control, RESTful APIs, signal-driven data consistency, audit logging, real-time notifications, and a clean multi-app Django architecture with 40+ apps.

---

## ✨ Features

### 🛒 Marketplace & Commerce
| Feature | Details |
|---------|---------|
| Multi-vendor marketplace | Browse, search, filter products by category |
| Shopping cart | Real-time stock validation, coupon support |
| Order lifecycle | Pending → Confirmed → Shipped → Delivered |
| Product reviews | Star ratings with verified-purchase badges |
| Wishlist | Save items for later |
| Coupon system | Discount codes with usage limits and expiry |

### 🏗️ Warehouse Operations
| Feature | Details |
|---------|---------|
| Inventory tracking | Stock levels, movements, low-stock alerts |
| Barcode & QR generation | Real Code128 + QR codes via `python-barcode` & `qrcode` |
| Stock adjustments | Damage write-offs, corrections, counts — with approval flow |
| Stock transfers | Move stock between warehouses with status tracking |
| Warehouse management | Multi-location support with images |
| Bulk CSV upload | Upload stock via template CSV |

### 📦 Rentals, Storage & Lockers
| Feature | Details |
|---------|---------|
| Equipment rental | Hourly/daily/weekly/monthly pricing, booking flow |
| Storage units | Book by size, duration, with capacity management |
| Smart lockers | Book, pay, access — with booking detail pages |
| Rental agreements | Auto-generated agreement pages per booking |
| Maintenance scheduling | Track maintenance for rental items |

### 💳 Payments & Billing
| Feature | Details |
|---------|---------|
| Unified payment flow | Same flow for orders, rentals, storage, lockers |
| Invoice generation | PDF-ready invoice and receipt templates |
| Payment history | Filterable history across all booking types |
| Refund processing | Role-gated refund workflow |
| COD support | Cash on delivery with pending payment status |

### 📊 Analytics & Reporting
| Feature | Details |
|---------|---------|
| Dashboard charts | Revenue, orders, stock levels — Chart.js |
| Advanced analytics | Heatmaps, bubble charts, time-series |
| Report generation | Exportable CSV and XLSX reports |
| Audit log | Every critical action is logged with user + timestamp |

### 💬 Communication & Support
| Feature | Details |
|---------|---------|
| Support tickets | Full ticket lifecycle: create → reply → resolve |
| Internal messaging | 1:1 and group chat for team members |
| Community forums | Topics, posts, threaded replies |
| Notification centre | In-app notifications with email integration |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | Django 4.2.11 |
| REST API | Django REST Framework 3.15 |
| Database | PostgreSQL 15 (production) / SQLite (dev) |
| Authentication | Django session auth + Django Allauth |
| Frontend | Bootstrap 5, vanilla JS, Chart.js |
| Static files | WhiteNoise (compressed, cached) |
| Barcode/QR | `python-barcode` 0.15, `qrcode` 7.4, Pillow 10 |
| Deployment | GitHub + Vercel (frontend demo) |
| WSGI server | Gunicorn 21 |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- pip
- Git

### Step 1 — Clone & install

```bash
git clone https://github.com/AshishCherian15/Multi-Stock-Logistics-Platform.git
cd Multi-Stock-Logistics-Platform

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Step 2 — Configure environment

```bash
cp .env.example .env
```

Edit `.env` — at minimum set:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

Generate a strong key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Step 3 — Migrate & seed

```bash
python manage.py migrate

python manage.py createsuperuser

# Optional: seed demo data
python manage.py populate_data
python manage.py seed_rentals
python manage.py seed_storage
python manage.py seed_lockers
python manage.py populate_coupons
```

### Step 4 — Run

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

---

## 📁 Project Structure

```
Multi-Stock-Logistics-Platform/
├── apps/
│   ├── auth_system/        # Login, register, password reset (OTP)
│   ├── orders/             # Sales & purchase orders, signals
│   ├── rentals/            # Equipment rental — booking & analytics
│   ├── storage/            # Storage unit bookings
│   ├── lockers/            # Smart locker booking system
│   ├── payments/           # Unified payment processor & history
│   ├── tickets/            # Support ticket system ← NEW
│   ├── reviews/            # Product reviews & ratings ← NEW
│   ├── adjustments/        # Stock adjustments with approval ← FIXED
│   ├── returns/            # Return requests & refunds ← FIXED
│   ├── transfers/          # Inter-warehouse stock transfers ← FIXED
│   ├── barcode/            # Real Code128 + QR generation ← FIXED
│   ├── analytics/          # Dashboard charts & metrics
│   ├── inventory/          # Inventory management
│   ├── billing/            # Invoices & receipts
│   ├── messaging/          # Internal chat (1:1 + groups)
│   ├── forums/             # Community forums
│   ├── notifications/      # Notification centre + email
│   ├── audit/              # Audit log middleware
│   ├── permissions/        # RBAC decorators & context processors
│   └── ...                 # 30+ more apps
├── templates/              # Django HTML templates (role-separated)
├── static/                 # CSS, JS, images
│   ├── css/                # Dark mode, sidebar, responsive, navbar
│   └── js/                 # Theme toggle, notifications, search, etc.
├── greaterwms/             # Django project — settings, urls, wsgi
├── frontend-vercel/        # Standalone Next.js frontend for Vercel deployment
├── media/                  # Product images (dev only)
├── fixtures/               # Seed data JSON
├── requirements.txt        # All packages pinned
└── manage.py
```

---

## 👥 Role-Based Access

| Role | Portal | Capabilities |
|------|--------|-------------|
| **Superadmin** | Team login | Full control — users, settings, analytics, purge |
| **Admin** | Team login | Orders, inventory, customers, reports, billing |
| **Supervisor** | Team login | Team management, bookings, approvals, returns |
| **Staff** | Team login | POS, shipping, day-to-day stock operations |
| **Customer** | Customer login | Marketplace, cart, orders, bookings, tickets |
| **Guest** | Guest access | Browse-only — marketplace, services, pricing |

---

## 🌐 Deployment (GitHub + Vercel Frontend)

This repository includes a separate frontend app in `frontend-vercel/` for public demo deployment.
The demo runs fully on Vercel using static exported data and does not require Render.

### 1. Push repository to GitHub

```bash
git init
git add .
git commit -m "Add full project with standalone Vercel frontend"
git branch -M main
git remote add origin https://github.com/<your-username>/Multi-Stock-Logistics-Platform.git
git push -u origin main
```

### 2. Deploy only frontend on Vercel

1. Open Vercel and import this GitHub repository.
2. Set **Root Directory** to `frontend-vercel`.
3. Framework is detected as Next.js.
4. No environment variables are required for demo deployment.
5. Click Deploy.

### 3. Frontend data source

- Frontend data file: `frontend-vercel/public/data/frontend_data.json`
- Data is extracted from Django and sanitized for frontend use.
- Sensitive auth/profile models are excluded from the Vercel dataset.

---

## 📡 API Reference

Base URL: `/api/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/goods/` | GET, POST | Products CRUD |
| `/api/warehouse/` | GET, POST | Warehouses |
| `/api/customer/` | GET, POST | Customers |
| `/api/supplier/` | GET, POST | Suppliers |
| `/api/notifications/` | GET | Notifications |
| `/api/dashboard-metrics/` | GET | Dashboard KPIs |
| `/api/dashboard-charts/` | GET | Chart data |
| `/api/search/` | GET | Global search |
| `/health/` | GET | Health check |

All API endpoints require authentication (session or token). Add `Authorization: Token <token>` header for token auth.

---

## 🧪 Running Tests

```bash
python manage.py test
```

---

## 👨‍💻 Author

**Ashish Cherian**
- USN: `4KM22CS018`
- Branch: B.E. Computer Science & Engineering
- Year: Final Year, 2025–26

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ using Django & Bootstrap

⭐ Star this repo if you found it useful!

</div>
