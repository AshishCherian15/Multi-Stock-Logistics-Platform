<div align="center">

# 🏭 Multi-Stock Logistics Platform

### Enterprise-Grade Warehouse & Logistics Management System

[![Django](https://img.shields.io/badge/Django-4.2.11-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**[🌐 Live Demo](#)** &nbsp;•&nbsp; **[🐛 Report Bug](https://github.com/AshishCherian15/Multi-Stock-Logistics-Platform/issues)** &nbsp;•&nbsp; **[💡 Request Feature](https://github.com/AshishCherian15/Multi-Stock-Logistics-Platform/issues)**

---

> *Final Year B.E. Computer Science & Engineering Project — 2025–26 | USN: 4KM22CS018*

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Screenshots](#-screenshots)
- [Login Credentials](#-login-credentials)
- [Project Structure](#-project-structure)
- [Frontend Deployment](#-frontend-deployment)
- [Database Management](#-database-management)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Author](#-author)

---

## 🧠 About

**Multi-Stock Logistics Platform** is a comprehensive, production-ready warehouse and logistics management system built with Django and PostgreSQL backend, with a Next.js frontend for modern deployment. It covers the full lifecycle of a logistics business — from inventory tracking and multi-vendor marketplace to equipment rentals, smart locker bookings, POS billing, analytics dashboards, and customer support.

Built as a Final Year CS Engineering project, it demonstrates enterprise software engineering patterns: role-based access control, RESTful APIs, signal-driven data consistency, audit logging, real-time notifications, and a clean multi-app Django architecture with 40+ apps.

---

## ✨ Features

### 🛒 Marketplace & Commerce
- Multi-vendor marketplace with search and filters
- Shopping cart with real-time stock validation
- Order lifecycle management (Pending → Confirmed → Shipped → Delivered)
- Product reviews with star ratings
- Wishlist and coupon system

### 🏗️ Warehouse Operations
- Inventory tracking with stock levels and movements
- Barcode & QR code generation
- Stock adjustments with approval workflow
- Multi-location warehouse support
- Bulk CSV upload

### 📦 Rentals, Storage & Lockers
- Equipment rental with flexible pricing (hourly/daily/weekly/monthly)
- Storage units booking by size and duration
- Smart lockers with booking management
- Automated rental agreements

### 💳 Payments & Billing
- Unified payment flow for all services
- Invoice and receipt generation
- Payment history tracking
- Refund processing workflow

### 📊 Analytics & Reporting
- Dashboard charts with Chart.js
- Advanced analytics with heatmaps
- Exportable CSV and XLSX reports
- Complete audit logging

### 💬 Communication & Support
- Support ticket system
- Internal messaging (1:1 and group chat)
- Community forums
- In-app notifications with email integration

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2.11, Django REST Framework 3.15 |
| Database | PostgreSQL 15 (production) / SQLite (dev) |
| Frontend | Next.js 14, React 18, CSS (custom + Bootstrap-style UI) |
| Authentication | Django session auth + DRF Token auth |
| Static Files | WhiteNoise (compressed, cached) |
| Barcode/QR | python-barcode 0.15, qrcode 7.4 |
| Deployment | Vercel (frontend), Render (backend via render.yaml) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- pip and npm
- Git

### Backend Setup (Django)

```bash
# Clone repository
git clone https://github.com/AshishCherian15/Multi-Stock-Logistics-Platform.git
cd Multi-Stock-Logistics-Platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set SECRET_KEY

# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed demo data (optional)
python manage.py populate_data
python manage.py seed_rentals
python manage.py seed_storage
python manage.py seed_lockers

# Export database for frontend
python export_simple.py

# Run development server
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

### Use the Included Demo Database (Optional)

This repository already includes `db.sqlite3` with preloaded demo data.

```bash
# If you want to use the included DB directly, just run:
python manage.py runserver
```

If you want a fresh database instead, delete `db.sqlite3`, then run `python manage.py migrate` and seed commands.

### Frontend Setup (Next.js)

```bash
# Navigate to frontend directory
cd frontend-vercel

# Install dependencies
npm install

# Run development server
npm run dev
```

Visit **http://localhost:3000**

---

## 🖼️ Screenshots

### Platform Preview Assets

| Module | Preview |
|--------|---------|
| Rental Equipment | ![Rental Equipment](static/images/rental_equipment.png) |
| Smart Lockers | ![Smart Locker](static/images/smart_locker.png) |
| Storage Units | ![Storage Unit](static/images/storage_unit.png) |

You can also capture your local UI screenshots after running both servers and add them under a folder like `docs/screenshots/`.

---

## 🔐 Login Credentials

### 🌐 Access URLs

**Django Backend (Local):**
- Main: `http://127.0.0.1:8000/`
- Login Selection: `http://127.0.0.1:8000/auth/login-selection/`
- Team Login: `http://127.0.0.1:8000/auth/team-login/`
- Customer Login: `http://127.0.0.1:8000/auth/customer-login/`
- Guest Access: `http://127.0.0.1:8000/guest/`

**Frontend (Local):**
- Main: `http://localhost:3000/`
- Login Selection: `http://localhost:3000/login-selection`
- Team Login: `http://localhost:3000/team-login`
- Customer Login: `http://localhost:3000/customer-login`

### 👥 Team Login Credentials

#### 🔴 SuperAdmin Accounts
**Full system access & management**

| Username | Password | Email |
|----------|----------|-------|
| `superuser` | `super123` | superuser@multistock.com |
| `testcustomer` | `super123` | testcustomer@multistock.com |

#### 🔵 Admin Accounts
**Administrative access**

| Username | Password | Email |
|----------|----------|-------|
| `admin` | `admin123` | admin@multistock.com |
| `admin_rajesh` | `admin123` | rajesh@multistock.com |
| `admin_priya` | `admin123` | priya@multistock.com |

#### 🟡 SubAdmin Accounts
**Supervisor access**

| Username | Password | Email |
|----------|----------|-------|
| `subadmin_suresh` | `sub123` | suresh@multistock.com |
| `senior_lakshmi` | `staff123` | lakshmi.senior@multistock.in |

#### 🟠 Staff Accounts
**Basic operations**

| Username | Password | Email |
|----------|----------|-------|
| `staff` | `staff123` | staff@multistock.com |
| `staff_amit` | `staff123` | amit@multistock.com |
| `staff_vikram` | `staff123` | vikram@multistock.com |

### 🛒 Customer Login Credentials

| Username | Password | Email |
|----------|----------|-------|
| `customer` | `customer123` | customer@example.com |
| `customer_arjun` | `customer123` | arjun@example.com |
| `customer_deepika` | `customer123` | deepika@example.com |

**Plus 46+ more customer accounts** (all with password: `customer123`)

### 🌍 Guest Access
No login required - browse-only access at `/guest/`

**📄 Complete credentials documentation:** See [CREDENTIALS.md](CREDENTIALS.md)

---

## 📁 Project Structure

```
Multi-Stock-Logistics-Platform/
├── apps/                       # Django apps (40+ apps)
│   ├── auth_system/           # Login, register, password reset
│   ├── orders/                # Sales & purchase orders
│   ├── rentals/               # Equipment rental system
│   ├── storage/               # Storage unit bookings
│   ├── lockers/               # Smart locker system
│   ├── payments/              # Unified payment processor
│   ├── tickets/               # Support ticket system
│   ├── reviews/               # Product reviews
│   ├── inventory/             # Inventory management
│   ├── analytics/             # Dashboard & metrics
│   └── ...                    # 30+ more apps
├── frontend-vercel/           # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js 14 app router
│   │   │   ├── login-selection/
│   │   │   ├── team-login/
│   │   │   ├── customer-login/
│   │   │   ├── products/
│   │   │   ├── rentals/
│   │   │   ├── storage/
│   │   │   └── lockers/
│   │   ├── components/       # Reusable components
│   │   └── lib/             # Utilities & data loaders
│   └── public/
│       └── data/            # Exported database JSON
├── templates/                # Django HTML templates
├── static/                   # CSS, JS, images
├── media/                    # Uploaded files
├── fixtures/                 # Seed data
├── greaterwms/              # Django project settings
├── export_simple.py         # Database export script
├── CREDENTIALS.md           # Complete login credentials
├── requirements.txt         # Python dependencies
├── manage.py
└── README.md
```

---

## 🌐 Frontend Deployment

### Deploy to Vercel

1. **Push to GitHub:**
```bash
git add .
git commit -m "Add complete project"
git push origin main
```

2. **Import to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your GitHub repository
   - Set **Root Directory** to `frontend-vercel`
   - Click "Deploy"

3. **Environment Variables (Optional):**
   - No environment variables needed for demo
   - Data is loaded from `/public/data/frontend_data.json`

### Local Frontend Development

```bash
cd frontend-vercel
npm install
npm run dev
```

### Build for Production

```bash
npm run build
npm start
```

### Backend Deployment (Render)

Backend Render deployment is configured through `render.yaml` in this repository.

- Keep `render.yaml` if you plan to deploy backend on Render.
- You can remove `render.yaml` only if you are certain backend deployment will be handled elsewhere.

The current configuration expects:
- Django app served by `gunicorn`
- `DATABASE_URL` (typically PostgreSQL, including Supabase PostgreSQL)
- CORS/CSRF origins for your frontend domain

---

## 💾 Database Management

### Export Database for Frontend

```bash
# Export all data to JSON
python export_simple.py
```

This creates `frontend-vercel/public/data/frontend_data.json` with:
- Products
- Stock Items
- Rentals
- Rental Categories
- Storage Units
- Lockers
- Locker Types
- Warehouses
- Orders
- Order Items
- Customers
- Suppliers
- Coupons

### Seed Demo Data

```bash
# Populate products
python manage.py populate_data

# Seed rentals
python manage.py seed_rentals

# Seed storage units
python manage.py seed_storage

# Seed lockers
python manage.py seed_lockers

# Seed coupons
python manage.py populate_coupons
```

### Reset Database

```bash
# Delete database
rm db.sqlite3

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed data
python manage.py populate_data
```

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

**Authentication:** Session-based or DRF Token-based
```bash
Authorization: Token <your-token>
```

---

## 🔧 Troubleshooting

### Login Not Working?
1. Verify correct login portal (Team vs Customer)
2. Check username spelling (case-sensitive)
3. Clear browser cache
4. Try incognito mode

### Database Issues?
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Frontend Not Loading Data?
```bash
# Re-export database
python export_simple.py

# Restart frontend
cd frontend-vercel
npm run dev
```

### Port Already in Use?
```bash
# Django (change port)
python manage.py runserver 8001

# Next.js (change port)
PORT=3001 npm run dev
```

---

## 🧪 Running Tests

```bash
# Django tests
python manage.py test

# Frontend quality check (lint)
cd frontend-vercel
npm run lint
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👨💻 Author

**Ashish Cherian**
- USN: `4KM22CS018`
- Branch: B.E. Computer Science & Engineering
- Year: Final Year, 2025–26
- GitHub: [@AshishCherian15](https://github.com/AshishCherian15)

---

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/AshishCherian15/Multi-Stock-Logistics-Platform/issues)
- **Email:** admin@multistock.com
- **Documentation:** [CREDENTIALS.md](CREDENTIALS.md)

---

<div align="center">

Made with ❤️ using Django, Next.js & PostgreSQL/SQLite

⭐ Star this repo if you found it useful!

**Last Updated:** March 2026 | **Version:** 2.1

</div>
