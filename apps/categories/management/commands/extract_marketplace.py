from django.core.management.base import BaseCommand
from goods.models import ListModel
from rentals.models import RentalItem, RentalCategory
from storage.models import StorageUnit
from lockers.models import Locker, LockerType

class Command(BaseCommand):
    help = 'Extract and display all marketplace data'

    def handle(self, *args, **options):
        print("\n" + "=" * 120)
        print("MARKETPLACE DATA EXTRACTION - COMPLETE INVENTORY")
        print("=" * 120)

        # PRODUCTS
        print("\n" + "=" * 120)
        print("PRODUCTS IN MARKETPLACE")
        print("=" * 120)
        products = ListModel.objects.filter(is_delete=False).order_by('goods_code')
        print(f"\nTotal Products: {products.count()}\n")
        print(f"{'Code':<20} | {'Description':<40} | {'Class':<20} | {'Brand':<20} | {'Price':<10}")
        print("-" * 120)
        for p in products:
            print(f"{p.goods_code:<20} | {p.goods_desc:<40} | {p.goods_class:<20} | {p.goods_brand:<20} | ${p.goods_price:<9.2f}")

        # RENTAL ITEMS
        print("\n" + "=" * 120)
        print("RENTAL EQUIPMENT")
        print("=" * 120)
        rental_categories = RentalCategory.objects.all()
        print(f"\nTotal Rental Categories: {rental_categories.count()}\n")
        for category in rental_categories:
            print(f"\n--- {category.name.upper()} ({category.category_type}) ---")
            rentals = RentalItem.objects.filter(category=category)
            print(f"Total Items: {rentals.count()}\n")
            print(f"{'Name':<40} | {'Status':<15} | {'Hourly':<10} | {'Daily':<10} | {'Weekly':<10} | {'Monthly':<10}")
            print("-" * 100)
            for r in rentals:
                print(f"{r.name:<40} | {r.status:<15} | ${r.hourly_rate:<9.2f} | ${r.daily_rate:<9.2f} | ${r.weekly_rate:<9.2f} | ${r.monthly_rate:<9.2f}")

        # STORAGE UNITS
        print("\n" + "=" * 120)
        print("STORAGE UNITS")
        print("=" * 120)
        storage_units = StorageUnit.objects.all().order_by('unit_number')
        print(f"\nTotal Storage Units: {storage_units.count()}\n")
        print(f"{'Unit Number':<15} | {'Type':<20} | {'Size (sqft)':<15} | {'Location':<30} | {'Price/Month':<15} | {'Climate':<10}")
        print("-" * 110)
        for s in storage_units:
            climate = "Yes" if s.is_climate_controlled else "No"
            print(f"{s.unit_number:<15} | {s.get_type_display():<20} | {s.size_sqft:<15} | {s.location:<30} | ${s.price_per_month:<14.2f} | {climate:<10}")

        # LOCKERS
        print("\n" + "=" * 120)
        print("SMART LOCKERS")
        print("=" * 120)
        locker_types = LockerType.objects.all()
        print(f"\nTotal Locker Types: {locker_types.count()}\n")
        for ltype in locker_types:
            print(f"\n--- {ltype.name.upper()} ({ltype.get_size_display()}) ---")
            lockers = Locker.objects.filter(locker_type=ltype)
            print(f"Total Lockers: {lockers.count()}")
            print(f"Hourly: ${ltype.hourly_rate} | Daily: ${ltype.daily_rate} | Weekly: ${ltype.weekly_rate} | Monthly: ${ltype.monthly_rate}\n")
            print(f"{'Locker #':<15} | {'Location':<30} | {'Status':<15}")
            print("-" * 65)
            for l in lockers:
                print(f"{l.locker_number:<15} | {l.location:<30} | {l.status:<15}")

        print("\n" + "=" * 120)
        print("EXTRACTION COMPLETE")
        print("=" * 120 + "\n")
