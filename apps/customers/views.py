from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from permissions.decorators import require_role
from orders.models import Order
from goods.models import ListModel as Product
from stock.models import StockListModel
from categories.models import Category

@login_required
def dashboard(request):
    """Customer dashboard; team roles redirect to management page"""
    from permissions.decorators import get_user_role
    user_role = get_user_role(request.user)
    if user_role in ['superadmin', 'admin', 'subadmin', 'staff']:
        return redirect('pages:customers')
    try:
        from cart.models import Cart
        cart = Cart.objects.get(user=request.user)
        cart_count = cart.items.count()
    except:
        cart_count = 0
    
    try:
        from wishlist.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    except:
        wishlist_count = 0
    
    # Get recent orders
    recent_orders = Order.objects.filter(customer_user=request.user).order_by('-created_at')[:5]
    
    # Get order status counts
    order_stats = Order.objects.filter(customer_user=request.user).values('status').annotate(count=Count('id'))
    
    context = {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'recent_orders': recent_orders,
        'order_stats': order_stats,
    }
    return render(request, 'customers/dashboard.html', context)

@login_required
@require_role('customer')
def marketplace(request):
    """Marketplace with products, search, and pagination"""
    products = Product.objects.filter(is_delete=False).order_by('goods_desc')
    categories = Category.objects.all()
    
    # Search
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(goods_desc__icontains=search) |
            Q(goods_code__icontains=search)
        )
    
    # Category filter
    category = request.GET.get('category')
    if category:
        products = products.filter(goods_class=category)
    
    # Pagination - increased to 24 items per page
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 24)  # 24 items per page (6x4 grid)
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Attach stock images to products
    for product in products_page:
        try:
            stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
            product.image = stock.goods_image if stock and stock.goods_image else None
        except:
            product.image = None
    
    try:
        from cart.models import Cart
        cart = Cart.objects.get(user=request.user)
        cart_count = cart.items.count()
    except:
        cart_count = 0
    
    try:
        from wishlist.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    except:
        wishlist_count = 0
    
    context = {
        'products': products_page,
        'categories': categories,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'search': search or '',
        'category': category,
    }
    return render(request, 'customers/marketplace.html', context)

@login_required
@require_role('customer')
def my_profile(request):
    """Customer profile page"""
    from profile.models import Profile
    from django.contrib import messages
    
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        if 'update_avatar' in request.POST:
            # Handle avatar upload
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
                profile.save()
                messages.success(request, 'Avatar updated successfully!')
                return redirect('customers:my_profile')
        else:
            # Handle profile update
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            
            profile.phone = request.POST.get('phone', '')
            profile.address = request.POST.get('address', '')
            if hasattr(profile, 'city'):
                profile.city = request.POST.get('city', '')
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('customers:my_profile')
    
    try:
        from cart.models import Cart
        cart = Cart.objects.get(user=request.user)
        cart_count = cart.items.count()
    except:
        cart_count = 0
    
    try:
        from wishlist.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    except:
        wishlist_count = 0
    
    context = {
        'user': request.user,
        'profile': profile,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'customers/my_profile.html', context)

@login_required
@require_role('customer')
def checkout(request):
    """Checkout page - create order from cart"""
    from cart.models import Cart
    from orders.models import Order, OrderItem
    from django.contrib import messages
    from payments.unified_payment import UnifiedPayment
    
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('cart:cart_page')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'online')
        
        order = Order.objects.create(
            order_type='sale',
            customer_user=request.user,
            status='pending',
            payment_status='unpaid',
            total_amount=cart.subtotal,
            delivery_fee=40,
            delivery_address=f"{request.POST.get('address')}, {request.POST.get('city')} - {request.POST.get('pincode')}",
            delivery_phone=request.POST.get('phone'),
            payment_method=payment_method,
            created_by=request.user
        )
        
        for cart_item in cart.items.all():
            if cart_item.item_type == 'product' and cart_item.product:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product_name,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    seller=cart_item.seller
                )
        
        cart.items.all().delete()
        
        result = UnifiedPayment.process_booking_payment(
            'order', order.id, order.total_amount, payment_method, request.user
        )
        
        if result['success']:
            messages.success(request, f'Order placed successfully! Order #{order.order_number}')
            return redirect('customers:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Payment failed. Please try again.')
            return redirect('customers:checkout')
    
    try:
        from wishlist.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    except:
        wishlist_count = 0
    
    context = {
        'cart': cart,
        'items': cart.items.all(),
        'subtotal': cart.subtotal,
        'grand_total': cart.subtotal + 40,
        'cart_count': cart.items.count(),
        'wishlist_count': wishlist_count,
    }
    return render(request, 'customers/checkout.html', context)

@login_required
@require_role('customer')
def mine(request):
    # Rentals
    try:
        from rentals.models import RentalBooking
        rentals = RentalBooking.objects.filter(customer=request.user).select_related('item', 'item__category')
        
        for rental in rentals:
            rental.equipment_name = rental.item.name
            rental.equipment_type = rental.item.category.name if rental.item.category else 'N/A'
            rental.booking_id = f"RB{rental.id:05d}"
            rental.total_cost = rental.total_amount
            rental.image = rental.item.image
            rental.status_color = {
                'active': 'success',
                'pending': 'warning',
                'completed': 'secondary',
                'cancelled': 'danger'
            }.get(rental.status, 'secondary')
    except:
        rentals = []
    
    # Storage
    try:
        from storage.models import StorageBooking
        bookings = StorageBooking.objects.filter(user=request.user).select_related('unit')
        
        storage_units = []
        for booking in bookings:
            unit = booking.unit
            unit.size = f"{unit.size_sqft} sq ft"
            unit.monthly_rate = unit.price_per_month
            unit.rental_start = booking.start_date
            unit.status = booking.status
            unit.status_color = {
                'active': 'success',
                'expired': 'danger',
                'cancelled': 'secondary'
            }.get(booking.status, 'secondary')
            storage_units.append(unit)
    except:
        storage_units = []
    
    # Lockers
    try:
        from lockers.models import LockerBooking
        bookings = LockerBooking.objects.filter(created_by=request.user).select_related('locker', 'locker__locker_type')
        
        lockers = []
        for booking in bookings:
            locker_data = type('obj', (object,), {
                'id': booking.id,
                'locker_number': booking.locker.locker_number,
                'size': booking.locker.locker_type.get_size_display(),
                'location': booking.locker.location,
                'rate': booking.total_amount,
                'rate_type': booking.duration_type,
                'booking_start': booking.start_date,
                'status': booking.status,
                'status_color': {
                    'active': 'success',
                    'pending': 'warning',
                    'completed': 'secondary',
                    'cancelled': 'danger'
                }.get(booking.status, 'secondary')
            })
            lockers.append(locker_data)
    except:
        lockers = []
    
    try:
        from cart.models import Cart
        cart = Cart.objects.get(user=request.user)
        cart_count = cart.items.count()
    except:
        cart_count = 0
    
    try:
        from wishlist.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    except:
        wishlist_count = 0
    
    context = {
        'rentals': rentals,
        'storage_units': storage_units,
        'lockers': lockers,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'customers/mine.html', context)

@login_required
@require_role('customer')
def my_orders(request):
    """Customer order history with pagination and filtering"""
    orders = Order.objects.filter(customer_user=request.user).order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status.lower())
    
    # Search
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search)
        )
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(orders, 10)  # 10 orders per page
    
    try:
        orders_page = paginator.page(page)
    except PageNotAnInteger:
        orders_page = paginator.page(1)
    except EmptyPage:
        orders_page = paginator.page(paginator.num_pages)
    
    try:
        from cart.models import Cart
        cart = Cart.objects.get(user=request.user)
        cart_count = cart.items.count()
    except:
        cart_count = 0
    
    try:
        from wishlist.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    except:
        wishlist_count = 0
    
    context = {
        'orders': orders_page,
        'status': status,
        'search': search or '',
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'customers/my_orders.html', context)

@login_required
@require_role('customer')
def order_detail(request, order_id):
    """Display detailed order information for customer"""
    from orders.models import Order
    
    order = get_object_or_404(Order, id=order_id, customer_user=request.user)
    items = order.items.all()
    status_history = order.status_history.all().order_by('-created_at')
    
    try:
        from cart.models import Cart
        cart = Cart.objects.get(user=request.user)
        cart_count = cart.items.count()
    except:
        cart_count = 0
    
    try:
        from wishlist.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    except:
        wishlist_count = 0
    
    context = {
        'order': order,
        'items': items,
        'status_history': status_history,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'customers/order_detail.html', context)

@login_required
@require_role('customer')
def my_rentals(request):
    # Redirect to mine page with rentals tab active
    return redirect('/customers/mine/?tab=rentals')

@login_required
@require_role('customer')
def my_storage(request):
    # Redirect to mine page with storage tab active
    return redirect('/customers/mine/?tab=storage')

@login_required
@require_role('customer')
def my_lockers(request):
    # Redirect to mine page with lockers tab active
    return redirect('/customers/mine/?tab=lockers')
