"""
Database Export Script for MultiStock Platform
Exports all data to JSON file for frontend deployment
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greaterwms.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.goods.models import ListModel as Product
from apps.rentals.models import RentalItem
from apps.storage.models import StorageUnit
from apps.lockers.models import Locker
from apps.warehouse.models import ListModel as Warehouse
from apps.coupons.models import Coupon
from apps.orders.models import Order
from apps.supplier.models import ListModel as Supplier

def export_database():
    """Export all relevant data to JSON"""
    data = {
        'users': [],
        'products': [],
        'rentals': [],
        'storage_units': [],
        'lockers': [],
        'warehouses': [],
        'coupons': [],
        'orders': [],
        'suppliers': []
    }
    
    # Export Users (excluding sensitive password data)
    for user in User.objects.all():
        try:
            profile = UserProfile.objects.get(user=user)
            role = profile.role
        except:
            role = 'customer' if not user.is_staff else 'admin'
        
        data['users'].append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': role,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None
        })
    
    # Export Products
    for product in Product.objects.all():
        data['products'].append({
            'id': product.id,
            'goods_code': product.goods_code,
            'goods_name': product.goods_name,
            'goods_desc': product.goods_desc,
            'goods_price': float(product.goods_price) if product.goods_price else 0,
            'goods_stock': product.goods_stock,
            'goods_image': product.goods_image.url if product.goods_image else None,
            'create_time': product.create_time.isoformat() if product.create_time else None
        })
    
    # Export Rentals
    for rental in RentalItem.objects.all():
        data['rentals'].append({
            'id': rental.id,
            'name': rental.name,
            'description': rental.description,
            'hourly_rate': float(rental.hourly_rate) if rental.hourly_rate else 0,
            'daily_rate': float(rental.daily_rate) if rental.daily_rate else 0,
            'weekly_rate': float(rental.weekly_rate) if rental.weekly_rate else 0,
            'monthly_rate': float(rental.monthly_rate) if rental.monthly_rate else 0,
            'image': rental.image.url if rental.image else None,
            'is_available': rental.is_available
        })
    
    # Export Storage Units
    for unit in StorageUnit.objects.all():
        data['storage_units'].append({
            'id': unit.id,
            'unit_number': unit.unit_number,
            'size': unit.size,
            'price_per_month': float(unit.price_per_month) if unit.price_per_month else 0,
            'description': unit.description,
            'image': unit.image.url if unit.image else None,
            'is_available': unit.is_available
        })
    
    # Export Lockers
    for locker in Locker.objects.all():
        data['lockers'].append({
            'id': locker.id,
            'locker_number': locker.locker_number,
            'size': locker.size,
            'hourly_rate': float(locker.hourly_rate) if locker.hourly_rate else 0,
            'daily_rate': float(locker.daily_rate) if locker.daily_rate else 0,
            'description': locker.description,
            'image': locker.image.url if locker.image else None,
            'is_available': locker.is_available
        })
    
    # Export Warehouses
    for warehouse in Warehouse.objects.all():
        data['warehouses'].append({
            'id': warehouse.id,
            'warehouse_name': warehouse.warehouse_name,
            'warehouse_city': warehouse.warehouse_city,
            'warehouse_address': warehouse.warehouse_address,
            'warehouse_contact': warehouse.warehouse_contact
        })
    
    # Export Coupons
    for coupon in Coupon.objects.all():
        data['coupons'].append({
            'id': coupon.id,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value) if coupon.discount_value else 0,
            'is_active': coupon.is_active,
            'valid_from': coupon.valid_from.isoformat() if coupon.valid_from else None,
            'valid_to': coupon.valid_to.isoformat() if coupon.valid_to else None
        })
    
    # Export Orders
    for order in Order.objects.all():
        data['orders'].append({
            'id': order.id,
            'order_number': order.order_number,
            'customer': order.customer.username if order.customer else None,
            'total_amount': float(order.total_amount) if order.total_amount else 0,
            'status': order.status,
            'created_at': order.created_at.isoformat() if order.created_at else None
        })
    
    # Export Suppliers
    for supplier in Supplier.objects.all():
        data['suppliers'].append({
            'id': supplier.id,
            'supplier_name': supplier.supplier_name,
            'supplier_city': supplier.supplier_city,
            'supplier_address': supplier.supplier_address,
            'supplier_contact': supplier.supplier_contact
        })
    
    # Save to file
    output_path = 'frontend-vercel/public/data/database_export.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Database exported successfully to {output_path}")
    print(f"📊 Exported:")
    print(f"   - {len(data['users'])} users")
    print(f"   - {len(data['products'])} products")
    print(f"   - {len(data['rentals'])} rental items")
    print(f"   - {len(data['storage_units'])} storage units")
    print(f"   - {len(data['lockers'])} lockers")
    print(f"   - {len(data['warehouses'])} warehouses")
    print(f"   - {len(data['coupons'])} coupons")
    print(f"   - {len(data['orders'])} orders")
    print(f"   - {len(data['suppliers'])} suppliers")
    
    return data

if __name__ == '__main__':
    export_database()
