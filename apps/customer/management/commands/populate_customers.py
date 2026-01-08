from django.core.management.base import BaseCommand
from customer.models import ListModel
import random

class Command(BaseCommand):
    help = 'Populate the database with real Indian customer data'

    def handle(self, *args, **options):
        # Define the customer data
        customers_data = [
            ("Aarav Gupta", "+91-98100-12345", "Self"),
            ("Aditya Gupta", "+91-99816-88990", "Self"),
            ("Aditya Kulkarni", "+91 96725 49501", "Sales Team"),
            ("Amit Ambani", "+91 87312 73848", "Sales Team"),
            ("Ananya Das", "+91-98300-55667", "Self"),
            ("Ananya Mittal", "+91 75563 41702", "Sales Team"),
            ("Aniket Kulkarni", "+91-99703-66778", "Self"),
            ("Arjun Mehta", "+91 73508 87140", "Sales Team"),
            ("Arjun Singh", "+91-99400-55566", "Self"),
            ("Devansh Roy", "+91-93080-55667", "Self"),
            ("Divya Nair", "+91 96764 50181", "Sales Team"),
            ("Harsh Vardhan", "+91-98990-33445", "Self"),
            ("Isha Verma", "+91-98200-34567", "Self"),
            ("Karan Malhotra", "+91 81398 32343", "Sales Team"),
            ("Karan Patel", "+91-99740-99900", "Self"),
            ("Kavita Deshmukh", "+91 86827 15564", "Sales Team"),
            ("Manish Tiwari", "+91 89279 40695", "Sales Team"),
            ("Meera Kapoor", "+91 96937 84932", "Sales Team"),
            ("Meera Pillai", "+91-98950-77889", "Self"),
            ("Neha Sharma", "+91-99220-33344", "Self"),
            ("Nikhil Rao", "+91-98230-11223", "Self"),
            ("Nikhil Saxena", "+91 79676 30919", "Sales Team"),
            ("Pooja Shah", "+91 90854 70821", "Sales Team"),
            ("Priya Nair", "+91-99890-77788", "Self"),
            ("Priyanka Jain", "+91 93356 23282", "Sales Team"),
            ("Rahul Jain", "+91-98110-66778", "Self"),
            ("Rahul Verma", "+91 83570 33123", "Sales Team"),
            ("Ritika Bose", "+91-97555-44556", "Self"),
            ("Ritu Agarwal", "+91 96146 28534", "Sales Team"),
            ("Riya Birla", "+91 95159 66789", "Sales Team"),
            ("Rohan Joshi", "+91 94344 94193", "Sales Team"),
            ("Rohan Mehta", "+91-98450-11122", "Self"),
            ("Sanjay Rao", "+91 81919 77921", "Sales Team"),
            ("Simran Kaur", "+91-98765-43210", "Self"),
            ("Sneha Iyer", "+91 70978 32108", "Sales Team"),
            ("Swati Bansal", "+91 98336 45305", "Sales Team"),
            ("Tanya Kapoor", "+91-98710-22334", "Self"),
            ("Vikram Rao", "+91-98290-22334", "Self"),
            ("Vikram Tata", "+91 70681 28225", "Sales Team"),
        ]

        # Indian cities for realistic data
        indian_cities = [
            "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
            "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
            "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal",
            "Visakhapatnam", "Vadodara", "Coimbatore", "Ludhiana", "Agra"
        ]

        # Street/area patterns for addresses
        street_patterns = [
            "MG Road", "Nehru Street", "Gandhi Nagar", "Park Street", "Residency Road",
            "Brigade Road", "Commercial Street", "Anna Salai", "Linking Road", "Main Road",
            "Sector {}", "Block {}", "Phase {}", "Hitech City", "Electronic City"
        ]

        area_patterns = [
            "Green Park", "South Extension", "Koramangala", "Indiranagar", "Whitefield",
            "Bandra West", "Andheri East", "Thane West", "Sector 15", "DLF Phase 3",
            "HSR Layout", "Jayanagar", "T Nagar", "Adyar", "Salt Lake City"
        ]

        created_count = 0
        updated_count = 0

        for name, contact, manager_type in customers_data:
            # Check if customer already exists
            existing = ListModel.objects.filter(customer_name=name).first()
            
            # Generate realistic address
            city = random.choice(indian_cities)
            street = random.choice(street_patterns)
            if '{}' in street:
                street = street.format(random.randint(1, 50))
            area = random.choice(area_patterns)
            address = f"{random.randint(1, 999)}, {street}, {area}, {city}"
            
            # Determine manager
            if manager_type == "Self":
                manager = "Self-Managed"
            else:
                # Assign a sales team member name
                sales_managers = [
                    "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sneha Reddy",
                    "Vikram Singh", "Anita Desai", "Suresh Nair", "Kavita Iyer"
                ]
                manager = random.choice(sales_managers)
            
            customer_data = {
                'customer_name': name,
                'customer_contact': contact,
                'customer_city': city,
                'customer_address': address,
                'customer_manager': manager,
                'customer_level': 1,
                'openid': '',
                'is_delete': False
            }
            
            if existing:
                # Update existing customer
                for key, value in customer_data.items():
                    setattr(existing, key, value)
                existing.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated: {name}'))
            else:
                # Create new customer
                ListModel.objects.create(**customer_data)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {name}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated customers!\n'
                f'  Created: {created_count}\n'
                f'  Updated: {updated_count}\n'
                f'  Total: {created_count + updated_count}'
            )
        )
