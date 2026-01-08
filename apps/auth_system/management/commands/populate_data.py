from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import datetime, timedelta
import random
from goods.models import ListModel as Product
from stock.models import StockListModel as Stock
from warehouse.models import ListModel as Warehouse
from customer.models import ListModel as Customer
from supplier.models import ListModel as Supplier
from multistock.models import Marketplace, Listing, Auction, Forum, ForumPost
from orders.models import Order, OrderItem
from expenses.models import Expense, ExpenseCategory

class Command(BaseCommand):
    help = 'Populate database with realistic sample data from August 20, 2025'

    def handle(self, *args, **options):
        start_date = datetime(2025, 8, 20, tzinfo=timezone.utc)
        
        # Create user hierarchy
        self.create_user_hierarchy()
        
        # Create sample data
        self.create_warehouses()
        self.create_customers()
        self.create_suppliers()
        self.create_products()
        self.create_stock()
        self.create_marketplaces()
        self.create_listings()
        self.create_auctions()
        self.create_forums()
        self.create_expenses()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data!'))
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('MULTISTOCK USER CREDENTIALS'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.WARNING('TEAM LOGIN ACCOUNTS:'))
        self.stdout.write('SuperAdmin: superadmin / super123 (Full System Access)')
        self.stdout.write('Admin: admin / admin123 (Administrative Access)')
        self.stdout.write('        self.stdout.write('Manager: manager / manager123 (Management Access)')
        self.stdout.write('Senior Staff: seniorstaff / senior123 (Senior Operations)')
        self.stdout.write('Staff: staff / staff123 (Basic Operations)')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('CUSTOMER LOGIN ACCOUNTS:'))
        self.stdout.write('Customer: customer / customer123 (Marketplace Access)')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Access: http://127.0.0.1:8000/'))
        self.stdout.write(self.style.SUCCESS('='*50))

    def create_user_hierarchy(self):
        # Create groups
        groups = ['SuperAdmin', 'Admin', 'SubAdmin', 'SeniorStaff', 'Staff', 'Customer']
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)

        # Create/Update admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@multistock.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if not created:
            admin_user.set_password('admin123')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
        else:
            admin_user.set_password('admin123')
            admin_user.save()
        admin_user.groups.add(Group.objects.get(name='Admin'))

        # Create hierarchy users
        users_data = [
            ('superadmin', 'super123', 'SuperAdmin', True, True),
            (, False, True),
            ('seniorstaff', 'senior123', 'SeniorStaff', False, True),
            ('staff', 'staff123', 'Staff', False, True),
            ('manager', 'manager123', 'SeniorStaff', False, True),
        ]
        
        for username, password, group_name, is_superuser, is_staff in users_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, f'{username}@multistock.com', password)
                user.is_superuser = is_superuser
                user.is_staff = is_staff
                user.save()
                user.groups.add(Group.objects.get(name=group_name))

        # Update customer user
        try:
            customer_user = User.objects.get(username='customer')
            customer_user.groups.add(Group.objects.get(name='Customer'))
        except User.DoesNotExist:
            customer_user = User.objects.create_user('customer', 'customer@multistock.com', 'customer123')
            customer_user.groups.add(Group.objects.get(name='Customer'))

    def create_warehouses(self):
        warehouses = [
            ('Main Warehouse NYC', 'New York', '123 Main St, NYC', 'John Manager', 'WH001'),
            ('West Coast Hub', 'Los Angeles', '456 West Ave, LA', 'Sarah Wilson', 'WH002'),
            ('Central Distribution', 'Chicago', '789 Central Blvd, Chicago', 'Mike Johnson', 'WH003'),
            ('East Coast Facility', 'Miami', '321 Ocean Dr, Miami', 'Lisa Brown', 'WH004'),
        ]
        
        for name, city, address, manager, code in warehouses:
            if not Warehouse.objects.filter(warehouse_name=name).exists():
                Warehouse.objects.create(
                    warehouse_name=name,
                    warehouse_city=city,
                    warehouse_address=address,
                    warehouse_contact='555-0123',
                    warehouse_manager=manager,
                    create_time=self.random_date()
                )

    def create_customers(self):
        customers = [
            ('TechCorp Solutions', 'San Francisco', '100 Tech St', '555-1001', 'Alice Tech'),
            ('Global Retail Inc', 'Dallas', '200 Retail Ave', '555-1002', 'Bob Retail'),
            ('Manufacturing Plus', 'Detroit', '300 Factory Rd', '555-1003', 'Carol Mfg'),
            ('E-Commerce Hub', 'Seattle', '400 Digital Way', '555-1004', 'David Online'),
            ('Supply Chain Pro', 'Atlanta', '500 Logistics Ln', '555-1005', 'Eva Supply'),
        ]
        
        for name, city, address, contact, manager in customers:
            if not Customer.objects.filter(customer_name=name).exists():
                Customer.objects.create(
                    customer_name=name,
                    customer_city=city,
                    customer_address=address,
                    customer_contact=contact,
                    customer_manager=manager,
                    customer_level=random.randint(1, 5),
                    create_time=self.random_date()
                )

    def create_suppliers(self):
        suppliers = [
            ('Electronics Wholesale', 'Shenzhen', '100 Electronics St', '555-2001', 'Zhang Wei'),
            ('Fashion Forward Ltd', 'Milan', '200 Fashion Ave', '555-2002', 'Marco Rossi'),
            ('Home & Garden Supply', 'Portland', '300 Garden Rd', '555-2003', 'Jennifer Green'),
            ('Sports Equipment Co', 'Denver', '400 Sports Way', '555-2004', 'Mike Athletic'),
            ('Office Solutions Inc', 'Boston', '500 Office Blvd', '555-2005', 'Susan Office'),
        ]
        
        for name, city, address, contact, manager in suppliers:
            if not Supplier.objects.filter(supplier_name=name).exists():
                Supplier.objects.create(
                    supplier_name=name,
                    supplier_city=city,
                    supplier_address=address,
                    supplier_contact=contact,
                    supplier_manager=manager,
                    supplier_level=random.randint(1, 5),
                    create_time=self.random_date()
                )

    def create_products(self):
        products = [
            ('iPhone 15 Pro', 'ELEC001', 'Electronics', 'Apple iPhone 15 Pro 256GB'),
            ('Samsung Galaxy S24', 'ELEC002', 'Electronics', 'Samsung Galaxy S24 Ultra 512GB'),
            ('MacBook Pro M3', 'ELEC003', 'Electronics', 'Apple MacBook Pro 14-inch M3'),
            ('Dell XPS 13', 'ELEC004', 'Electronics', 'Dell XPS 13 Laptop Intel i7'),
            ('Nike Air Max', 'FASH001', 'Fashion', 'Nike Air Max 270 Running Shoes'),
            ('Adidas Ultraboost', 'FASH002', 'Fashion', 'Adidas Ultraboost 22 Sneakers'),
            ('Levi\'s Jeans', 'FASH003', 'Fashion', 'Levi\'s 501 Original Fit Jeans'),
            ('North Face Jacket', 'FASH004', 'Fashion', 'The North Face Venture 2 Jacket'),
            ('Garden Hose 50ft', 'HOME001', 'Home & Garden', 'Heavy Duty Garden Hose 50 feet'),
            ('Lawn Mower Electric', 'HOME002', 'Home & Garden', 'Electric Cordless Lawn Mower'),
        ]
        
        for name, code, category, desc in products:
            if not Product.objects.filter(goods_code=code).exists():
                Product.objects.create(
                    goods_code=code,
                    goods_desc=name,
                    goods_supplier=desc,
                    goods_weight=random.uniform(0.5, 10.0),
                    goods_w=random.uniform(10, 50),
                    goods_d=random.uniform(10, 50),
                    goods_h=random.uniform(5, 30),
                    unit_cost=random.uniform(50, 2000),
                    goods_unit='pcs',
                    goods_class=category,
                    goods_brand=name.split()[0],
                    goods_color='Mixed',
                    goods_shape='Standard',
                    goods_specs=desc,
                    goods_origin='Global',
                    safety_stock=random.randint(10, 100),
                    create_time=self.random_date()
                )

    def create_stock(self):
        products = Product.objects.all()
        warehouses = Warehouse.objects.all()
        
        for product in products:
            for warehouse in warehouses:
                if not Stock.objects.filter(goods_code=product.goods_code, warehouse_name=warehouse.warehouse_name).exists():
                    Stock.objects.create(
                        goods_code=product.goods_code,
                        goods_desc=product.goods_desc,
                        goods_qty=random.randint(50, 500),
                        goods_shelf_to_shelf='A' + str(random.randint(1, 20)),
                        warehouse_name=warehouse.warehouse_name,
                        create_time=self.random_date()
                    )

    def create_marketplaces(self):
        marketplaces = [
            ('Global Electronics Hub', 'Premier marketplace for electronic devices'),
            ('Fashion Central', 'Latest trends in fashion and accessories'),
            ('Home & Garden Paradise', 'Everything for your home and garden needs'),
        ]
        
        admin_user = User.objects.get(username='admin')
        for name, desc in marketplaces:
            if not Marketplace.objects.filter(name=name).exists():
                Marketplace.objects.create(
                    name=name,
                    description=desc,
                    owner=admin_user,
                    created_at=self.random_date()
                )

    def create_listings(self):
        marketplaces = Marketplace.objects.all()
        products = Product.objects.all()
        users = User.objects.filter(is_staff=True)
        
        for _ in range(20):
            product = random.choice(products)
            marketplace = random.choice(marketplaces)
            seller = random.choice(users)
            
            Listing.objects.create(
                marketplace=marketplace,
                product_code=product.goods_code,
                title=f"{product.goods_desc} - Premium Quality",
                description=f"High-quality {product.goods_desc} available for immediate shipping.",
                price=product.unit_cost * random.uniform(1.2, 2.0),
                quantity=random.randint(1, 50),
                seller=seller,
                created_at=self.random_date()
            )

    def create_auctions(self):
        products = Product.objects.all()
        users = User.objects.filter(is_staff=True)
        
        for _ in range(10):
            product = random.choice(products)
            seller = random.choice(users)
            start_price = product.unit_cost * 0.8
            
            Auction.objects.create(
                product_code=product.goods_code,
                title=f"Auction: {product.goods_desc}",
                starting_price=start_price,
                current_price=start_price * random.uniform(1.0, 1.5),
                end_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                seller=seller,
                created_at=self.random_date()
            )

    def create_forums(self):
        forums = [
            ('General Discussion', 'General platform discussions'),
            ('Product Reviews', 'Share your product experiences'),
            ('Technical Support', 'Get help with technical issues'),
            ('Business Tips', 'Share business insights and tips'),
        ]
        
        admin_user = User.objects.get(username='admin')
        for title, desc in forums:
            if not Forum.objects.filter(title=title).exists():
                forum = Forum.objects.create(
                    title=title,
                    description=desc,
                    creator=admin_user,
                    created_at=self.random_date()
                )
                
                # Add some posts
                users = User.objects.all()
                for _ in range(random.randint(3, 8)):
                    ForumPost.objects.create(
                        forum=forum,
                        author=random.choice(users),
                        content=f"This is a sample post in {title} forum. Great discussion topic!",
                        created_at=self.random_date()
                    )

    def create_expenses(self):
        # Create expense categories
        categories = [
            ('Office Supplies', 'Monthly office supply expenses'),
            ('Utilities', 'Electricity and water bills'),
            ('Marketing', 'Digital marketing campaigns'),
            ('Transportation', 'Shipping and logistics costs'),
            ('Equipment', 'New equipment purchases'),
        ]
        
        for name, desc in categories:
            ExpenseCategory.objects.get_or_create(name=name, defaults={'description': desc})
        
        # Create expenses
        warehouses = Warehouse.objects.all()
        categories_objs = ExpenseCategory.objects.all()
        admin_user = User.objects.get(username='admin')
        
        for i in range(30):
            if warehouses and categories_objs:
                Expense.objects.get_or_create(
                    reference=f'EXP-2025-{i+1:03d}',
                    defaults={
                        'date': self.random_date().date(),
                        'warehouse': random.choice(warehouses),
                        'category': random.choice(categories_objs),
                        'amount': random.uniform(100, 5000),
                        'details': f'Sample expense for {random.choice(categories_objs).name}',
                        'created_by': admin_user
                    }
                )

    def random_date(self):
        start_date = datetime(2025, 8, 20, tzinfo=timezone.utc)
        end_date = timezone.now()
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between + 1)
        return start_date + timedelta(days=random_days)
