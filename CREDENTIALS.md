# 🔐 MultiStock Platform - Login Credentials

## 📋 Overview
This document contains all login credentials for the MultiStock Logistics Platform.
All passwords are for **DEMO/DEVELOPMENT purposes only**.

---

## 🌐 Access URLs

### Django Backend (Local Development)
- **URL**: `http://127.0.0.1:8000/`
- **Login Selection**: `http://127.0.0.1:8000/auth/login-selection/`
- **Team Login**: `http://127.0.0.1:8000/auth/team-login/`
- **Customer Login**: `http://127.0.0.1:8000/auth/customer-login/`
- **Guest Access**: `http://127.0.0.1:8000/guest/`

### Frontend (Vercel Deployment)
- **URL**: `https://your-app.vercel.app/`
- **Login Selection**: `/login-selection`
- **Team Login**: `/team-login`
- **Customer Login**: `/customer-login`

---

## 👥 Team Login Credentials

### 🔴 SuperAdmin Accounts
**Full system access & management**

| Username | Password | Email | Role |
|----------|----------|-------|------|
| `superuser` | `super123` | superuser@multistock.com | SuperAdmin |
| `testcustomer` | `super123` | testcustomer@multistock.com | SuperAdmin |

**Access Includes:**
- System settings & configurations
- Automation workflows
- All warehouses & suppliers
- User roles & permissions
- Advanced analytics & reports
- Database management
- Purge data operations

---

### 🔵 Admin Accounts
**Administrative access for operations management**

| Username | Password | Email | Role |
|----------|----------|-------|------|
| `admin` | `admin123` | admin@multistock.com | Admin |
| `admin_rajesh` | `admin123` | rajesh@multistock.com | Admin |
| `admin_priya` | `admin123` | priya@multistock.com | Admin |

**Access Includes:**
- Inventory management
- Order controls & approvals
- Workflow management
- Financial reporting
- Supplier relationships
- Product management
- Rental operations
- Storage unit controls
- Marketplace operations
- Department analytics

---

### 🟡 SubAdmin Accounts
**Supervisor/Store manager access**

| Username | Password | Email | Role |
|----------|----------|-------|------|
| `subadmin_suresh` | `sub123` | suresh@multistock.com | SubAdmin |
| `senior_lakshmi` | `staff123` | lakshmi.senior@multistock.in | SubAdmin |

**Access Includes:**
- Rental management
- Locker operations
- Order processing
- Task tracking
- Team coordination
- Daily operations oversight

---

### 🟠 Staff Accounts
**Basic staff operations**

| Username | Password | Email | Role |
|----------|----------|-------|------|
| `staff` | `staff123` | staff@multistock.com | Staff |
| `staff_amit` | `staff123` | amit@multistock.com | Staff |
| `staff_vikram` | `staff123` | vikram@multistock.com | Staff |
| `superadmin` | `staff123` | superadmin@multistock.com | Staff |

**Access Includes:**
- Check-ins & checkouts
- Barcode scanning
- Storage logs
- Task assignments
- Basic reporting

---

## 🛒 Customer Login Credentials

### 🟢 Customer Accounts
**Marketplace & shopping access**

| Username | Password | Email | Role |
|----------|----------|-------|------|
| `customer` | `customer123` | customer@example.com | Customer |
| `customer_arjun` | `customer123` | arjun@example.com | Customer |
| `customer_deepika` | `customer123` | deepika@example.com | Customer |

**Plus 46+ more customer accounts** (all with password: `customer123`)

**Access Includes:**
- Browse & order products
- Rental bookings
- Storage unit reservations
- Auction participation
- Subscription plans & coupons
- Order tracking
- Wishlist management
- Product reviews

---

## 🌍 Guest Access

**No login required** - Browse-only access

**Access Includes:**
- Browse marketplace & products
- View live auctions
- Read community forums
- Access analytics dashboard
- View inventory catalog

**URL**: `http://127.0.0.1:8000/guest/` or `/guest` on frontend

---

## 🔧 Testing Credentials

### Quick Test Accounts

**For SuperAdmin Testing:**
```
Username: superuser
Password: super123
```

**For Admin Testing:**
```
Username: admin
Password: admin123
```

**For Customer Testing:**
```
Username: customer
Password: customer123
```

**For Staff Testing:**
```
Username: staff
Password: staff123
```

---

## 🚀 How to Login

### Step 1: Choose Login Path
Visit the login selection page and choose your role:
- **Team Login** - For staff, managers, and administrators
- **Customer Login** - For customers
- **Guest Access** - Browse without login

### Step 2: Enter Credentials
Use any of the credentials listed above based on your role.

### Step 3: Access Dashboard
You'll be redirected to your role-specific dashboard with appropriate permissions.

---

## 🔒 Security Notes

⚠️ **IMPORTANT**: These credentials are for **DEMO/DEVELOPMENT purposes only**.

For production deployment:
1. Change all default passwords
2. Implement strong password policies
3. Enable two-factor authentication
4. Use environment variables for sensitive data
5. Implement rate limiting on login endpoints
6. Enable HTTPS/SSL
7. Regular security audits

---

## 📝 Password Reset

If you forget your password:
1. Click "Forgot Password?" on the login page
2. Enter your email address
3. Follow the reset link sent to your email

**Note**: Email functionality requires SMTP configuration in `.env` file.

---

## 🆘 Troubleshooting

### Login Not Working?
1. Verify you're using the correct login portal (Team vs Customer)
2. Check username spelling (case-sensitive)
3. Ensure password is correct
4. Clear browser cache and cookies
5. Try incognito/private browsing mode

### Account Locked?
Contact system administrator or use the superuser account to unlock.

### Database Issues?
Run migrations:
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 📊 Database Export

To export current database for frontend:
```bash
python export_simple.py
```

This creates `frontend-vercel/public/data/frontend_data.json` with all data.

---

## 📞 Support

For issues or questions:
- **GitHub Issues**: [Report Bug](https://github.com/AshishCherian15/Multi-Stock-Logistics-Platform/issues)
- **Email**: admin@multistock.com
- **Documentation**: See README.md

---

**Last Updated**: January 2025
**Version**: 2.0
**Author**: Ashish Cherian (USN: 4KM22CS018)
