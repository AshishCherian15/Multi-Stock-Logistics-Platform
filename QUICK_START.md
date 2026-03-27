# ⚡ Quick Setup Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Clone & Setup Backend (2 minutes)

```bash
# Clone repository
git clone https://github.com/AshishCherian15/Multi-Stock-Logistics-Platform.git
cd Multi-Stock-Logistics-Platform

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

✅ **Backend running at:** http://127.0.0.1:8000/

---

### Step 2: Setup Frontend (2 minutes)

```bash
# Open new terminal
cd frontend-vercel

# Install dependencies
npm install

# Start dev server
npm run dev
```

✅ **Frontend running at:** http://localhost:3000/

---

### Step 3: Login & Explore (1 minute)

**Quick Test Credentials:**

| Role | Username | Password | URL |
|------|----------|----------|-----|
| SuperAdmin | `superuser` | `super123` | http://127.0.0.1:8000/auth/team-login/ |
| Admin | `admin` | `admin123` | http://127.0.0.1:8000/auth/team-login/ |
| Customer | `customer` | `customer123` | http://127.0.0.1:8000/auth/customer-login/ |
| Guest | *(no login)* | - | http://127.0.0.1:8000/guest/ |

---

## 🎯 Common Tasks

### Export Database for Frontend
```bash
python export_simple.py
```

### Seed Demo Data
```bash
python manage.py populate_data
python manage.py seed_rentals
python manage.py seed_storage
python manage.py seed_lockers
```

### Reset Database
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py populate_data
```

### Deploy Frontend to Vercel
```bash
# Push to GitHub
git add .
git commit -m "Deploy frontend"
git push origin main

# Then:
# 1. Go to vercel.com
# 2. Import repository
# 3. Set root directory: frontend-vercel
# 4. Deploy
```

---

## 📋 Access URLs

### Django Backend (Local)
- **Main:** http://127.0.0.1:8000/
- **Login Selection:** http://127.0.0.1:8000/auth/login-selection/
- **Team Login:** http://127.0.0.1:8000/auth/team-login/
- **Customer Login:** http://127.0.0.1:8000/auth/customer-login/
- **Guest:** http://127.0.0.1:8000/guest/
- **Admin Panel:** http://127.0.0.1:8000/admin/

### Next.js Frontend (Local)
- **Main:** http://localhost:3000/
- **Login Selection:** http://localhost:3000/login-selection
- **Products:** http://localhost:3000/products
- **Rentals:** http://localhost:3000/rentals
- **Storage:** http://localhost:3000/storage
- **Lockers:** http://localhost:3000/lockers

---

## 🔐 All Login Credentials

### 🔴 SuperAdmin (Full Access)
```
superuser / super123
testcustomer / super123
```

### 🔵 Admin (Management)
```
admin / admin123
admin_rajesh / admin123
admin_priya / admin123
```

### 🟡 SubAdmin (Supervisor)
```
subadmin_suresh / sub123
senior_lakshmi / staff123
```

### 🟠 Staff (Operations)
```
staff / staff123
staff_amit / staff123
staff_vikram / staff123
```

### 🟢 Customer (Shopping)
```
customer / customer123
customer_arjun / customer123
customer_deepika / customer123
+ 46 more accounts (all password: customer123)
```

**📄 Complete list:** See [CREDENTIALS.md](CREDENTIALS.md)

---

## 🐛 Troubleshooting

### Port Already in Use?
```bash
# Django - use different port
python manage.py runserver 8001

# Next.js - use different port
PORT=3001 npm run dev
```

### Database Locked?
```bash
# Close all Django processes
# Delete db.sqlite3
# Run migrations again
python manage.py migrate
```

### Frontend Not Loading?
```bash
# Clear Next.js cache
cd frontend-vercel
rm -rf .next
npm run dev
```

### Login Not Working?
1. Check you're using correct portal (Team vs Customer)
2. Verify username/password spelling
3. Clear browser cache
4. Try incognito mode

---

## 📚 Documentation

- **README.md** - Complete project documentation
- **CREDENTIALS.md** - All login credentials
- **PROJECT_UPDATES.md** - Recent changes and updates
- **This file** - Quick setup guide

---

## 🆘 Need Help?

**GitHub Issues:** https://github.com/AshishCherian15/Multi-Stock-Logistics-Platform/issues

**Email:** admin@multistock.com

---

## ✅ Checklist

After setup, verify:

- [ ] Django server running on port 8000
- [ ] Next.js server running on port 3000
- [ ] Can access login selection page
- [ ] Can login with test credentials
- [ ] Database has demo data
- [ ] Frontend loads data from JSON

---

**Last Updated:** January 2025
**Version:** 2.0
**Author:** Ashish Cherian
