from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from django.db.utils import OperationalError
import time
from goods.models import ListModel as Product
from stock.models import StockListModel, StockMovement, StockAlert
from orders.models import Order, OrderItem, OrderStatusHistory
from customer.models import ListModel as Customer
from supplier.models import ListModel as Supplier
from warehouse.models import ListModel as Warehouse
# from multistock.models import Listing, Auction, Bid, Forum, ForumPost
from billing.models import Invoice, InvoiceItem, Receipt
from expenses.models import Expense
from credit.models import CreditProfile, CreditTransaction
from coupons.models import Coupon
from pos.models import POSSale, POSSaleItem
from rentals.models import RentalItem, RentalBooking, MaintenanceSchedule
from storage.models import StorageUnit, StorageBooking

# Import RBAC decorators
from permissions.decorators import require_role

@require_role('superadmin')  # Only SuperAdmin can purge data
def purge_data(request):
    if request.method == 'POST':
        modules = request.POST.getlist('modules')
        
        try:
            connection.close()
            time.sleep(0.1)
            
            purged = []
            
            if 'products' in modules:
                try:
                    count = Product.objects.all().delete()[0]
                    purged.append(f'Products: {count}')
                except OperationalError:
                    pass
            
            if 'stocks' in modules:
                try:
                    count = StockListModel.objects.all().delete()[0]
                    StockMovement.objects.all().delete()
                    StockAlert.objects.all().delete()
                    purged.append(f'Stocks: {count}')
                except OperationalError:
                    pass
            
            if 'orders' in modules:
                try:
                    OrderItem.objects.all().delete()
                    OrderStatusHistory.objects.all().delete()
                    count = Order.objects.all().delete()[0]
                    purged.append(f'Orders: {count}')
                except OperationalError:
                    pass
            
            if 'customers' in modules:
                try:
                    count = Customer.objects.all().delete()[0]
                    purged.append(f'Customers: {count}')
                except OperationalError:
                    pass
            
            if 'suppliers' in modules:
                try:
                    count = Supplier.objects.all().delete()[0]
                    purged.append(f'Suppliers: {count}')
                except OperationalError:
                    pass
            
            if 'warehouses' in modules:
                try:
                    count = Warehouse.objects.all().delete()[0]
                    purged.append(f'Warehouses: {count}')
                except OperationalError:
                    pass
            
            # if 'marketplace' in modules:
            #     try:
            #         count = Listing.objects.all().delete()[0]
            #         purged.append(f'Marketplace Listings: {count}')
            #     except OperationalError:
            #         pass
            # 
            # if 'auctions' in modules:
            #     try:
            #         Bid.objects.all().delete()
            #         count = Auction.objects.all().delete()[0]
            #         purged.append(f'Auctions: {count}')
            #     except OperationalError:
            #         pass
            
            if 'invoices' in modules:
                try:
                    InvoiceItem.objects.all().delete()
                    Receipt.objects.all().delete()
                    count = Invoice.objects.all().delete()[0]
                    purged.append(f'Invoices: {count}')
                except OperationalError:
                    pass
            
            if 'expenses' in modules:
                try:
                    count = Expense.objects.all().delete()[0]
                    purged.append(f'Expenses: {count}')
                except OperationalError:
                    pass
            
            if 'credit' in modules:
                try:
                    CreditTransaction.objects.all().delete()
                    count = CreditProfile.objects.all().delete()[0]
                    purged.append(f'Credit Entries: {count}')
                except OperationalError:
                    pass
            
            if 'coupons' in modules:
                try:
                    count = Coupon.objects.all().delete()[0]
                    purged.append(f'Coupons: {count}')
                except OperationalError:
                    pass
            
            if 'pos' in modules:
                try:
                    POSSaleItem.objects.all().delete()
                    count = POSSale.objects.all().delete()[0]
                    purged.append(f'POS Sales: {count}')
                except OperationalError:
                    pass
            
            if 'rentals' in modules:
                try:
                    RentalBooking.objects.all().delete()
                    MaintenanceSchedule.objects.all().delete()
                    count = RentalItem.objects.all().delete()[0]
                    purged.append(f'Rental Items: {count}')
                except OperationalError:
                    pass
            
            if 'storage' in modules:
                try:
                    StorageBooking.objects.all().delete()
                    count = StorageUnit.objects.all().delete()[0]
                    purged.append(f'Storage Units: {count}')
                except OperationalError:
                    pass
            
            # if 'forums' in modules:
            #     try:
            #         ForumPost.objects.all().delete()
            #         count = Forum.objects.all().delete()[0]
            #         purged.append(f'Forums: {count}')
            #     except OperationalError:
            #         pass
            
            if purged:
                messages.success(request, f'Data purged successfully: {", ".join(purged)}')
            else:
                messages.warning(request, 'No data was purged. Selected modules may be empty or tables do not exist.')
        except Exception as e:
            messages.error(request, f'Error purging data: {str(e)}')
        
        return redirect('purge_data')
    
    # Helper function to safely count model instances
    def safe_count(model):
        try:
            return model.objects.count()
        except OperationalError:
            return 0
    
    counts = {
        'products': safe_count(Product),
        'stocks': safe_count(StockListModel),
        'orders': safe_count(Order),
        'customers': safe_count(Customer),
        'suppliers': safe_count(Supplier),
        'warehouses': safe_count(Warehouse),
        # 'marketplace': safe_count(Listing),
        # 'auctions': safe_count(Auction),
        'invoices': safe_count(Invoice),
        'expenses': safe_count(Expense),
        'credit': safe_count(CreditProfile),
        'coupons': safe_count(Coupon),
        'pos': safe_count(POSSale),
        'rentals': safe_count(RentalItem),
        'storage': safe_count(StorageUnit),
        # 'forums': safe_count(Forum),
    }
    
    return render(request, 'admin/purge_data.html', {'counts': counts})
