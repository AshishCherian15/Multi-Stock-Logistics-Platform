"""
Simple Database Export Script
Exports data using Django's dumpdata command
"""
import subprocess
import json
import os

def export_data():
    """Export database to JSON"""
    
    # Models to export
    models = [
        'goods.ListModel',
        'stock.StockListModel',
        'warehouse.ListModel',
        'customer.ListModel',
        'supplier.ListModel',
        'orders.Order',
        'orders.OrderItem',
        'rentals.RentalCategory',
        'rentals.RentalItem',
        'storage.StorageUnit',
        'lockers.LockerType',
        'lockers.Locker',
        'coupons.Coupon',
    ]
    
    output_dir = 'frontend-vercel/public/data'
    os.makedirs(output_dir, exist_ok=True)
    
    all_data = []
    
    for model in models:
        try:
            result = subprocess.run(
                ['python', 'manage.py', 'dumpdata', model, '--indent', '2'],
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)
            all_data.extend(data)
            print(f"[OK] Exported {len(data)} records from {model}")
        except Exception as e:
            print(f"[SKIP] Skipped {model}: {str(e)}")
    
    # Save combined data
    output_file = os.path.join(output_dir, 'frontend_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n[OK] Total {len(all_data)} records exported to {output_file}")

if __name__ == '__main__':
    export_data()
