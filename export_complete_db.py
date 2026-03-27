import os
import sys
import django
import json

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greaterwms.settings')
django.setup()

from django.core import serializers
from django.contrib.auth.models import User
from apps.goods.models import ListModel as Product
from apps.rentals.models import RentalItem
from apps.storage.models import StorageUnit
from apps.lockers.models import Locker
from apps.warehouse.models import ListModel as Warehouse
from apps.orders.models import Order
from apps.supplier.models import ListModel as Supplier

def export_complete_database():
    """Export complete database to JSON with UTF-8 encoding"""
    
    print("Starting database export...")
    
    all_data = []
    
    # Export Users
    print("Exporting users...")
    users = User.objects.all()
    user_data = json.loads(serializers.serialize('json', users))
    all_data.extend(user_data)
    print(f"  Exported {len(user_data)} users")
    
    # Export Products
    print("Exporting products...")
    products = Product.objects.all()
    product_data = json.loads(serializers.serialize('json', products))
    all_data.extend(product_data)
    print(f"  Exported {len(product_data)} products")
    
    # Export Rentals
    print("Exporting rentals...")
    rentals = RentalItem.objects.all()
    rental_data = json.loads(serializers.serialize('json', rentals))
    all_data.extend(rental_data)
    print(f"  Exported {len(rental_data)} rental items")
    
    # Export Storage Units
    print("Exporting storage units...")
    storage = StorageUnit.objects.all()
    storage_data = json.loads(serializers.serialize('json', storage))
    all_data.extend(storage_data)
    print(f"  Exported {len(storage_data)} storage units")
    
    # Export Lockers
    print("Exporting lockers...")
    lockers = Locker.objects.all()
    locker_data = json.loads(serializers.serialize('json', lockers))
    all_data.extend(locker_data)
    print(f"  Exported {len(locker_data)} lockers")
    
    # Export Warehouses
    print("Exporting warehouses...")
    warehouses = Warehouse.objects.all()
    warehouse_data = json.loads(serializers.serialize('json', warehouses))
    all_data.extend(warehouse_data)
    print(f"  Exported {len(warehouse_data)} warehouses")
    
    # Export Orders
    print("Exporting orders...")
    orders = Order.objects.all()
    order_data = json.loads(serializers.serialize('json', orders))
    all_data.extend(order_data)
    print(f"  Exported {len(order_data)} orders")
    
    # Export Suppliers
    print("Exporting suppliers...")
    suppliers = Supplier.objects.all()
    supplier_data = json.loads(serializers.serialize('json', suppliers))
    all_data.extend(supplier_data)
    print(f"  Exported {len(supplier_data)} suppliers")
    
    # Save to fixtures directory
    output_path = 'fixtures/complete_database.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SUCCESS] Exported {len(all_data)} total records to {output_path}")
    
    # Also save to frontend
    frontend_path = 'frontend-vercel/public/data/frontend_data.json'
    os.makedirs(os.path.dirname(frontend_path), exist_ok=True)
    
    with open(frontend_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"[SUCCESS] Also saved to {frontend_path}")
    
    return all_data

if __name__ == '__main__':
    export_complete_database()
