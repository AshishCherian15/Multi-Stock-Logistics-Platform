from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

def guest_home(request):
    """Redirect guest root to dashboard"""
    return redirect('/guest/dashboard/')


def browse_products(request):
    """Browse products as guest"""
    from goods.models import ListModel as Product
    from stock.models import StockListModel
    
    products = Product.objects.filter(is_delete=False).order_by('goods_desc')
    
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
    
    # Limit to 50 for guests
    products = products[:50]
    
    # Add stock images to products
    products_with_images = []
    for product in products:
        stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
        product.stock_image = None
        if stock and stock.goods_image:
            try:
                if hasattr(stock.goods_image, 'url'):
                    product.stock_image = stock.goods_image.url
                else:
                    product.stock_image = f'/media/{stock.goods_image}'
            except:
                pass
        products_with_images.append(product)
    
    # Get categories
    categories = Product.objects.filter(is_delete=False).values_list('goods_class', flat=True).distinct()
    
    context = {
        'products': products_with_images,
        'categories': categories,
        'total_products': len(products_with_images),
    }
    
    return render(request, 'guest/products.html', context)


def product_detail_guest(request, product_id):
    """View product details as guest"""
    from goods.models import ListModel as Product
    from stock.models import StockListModel
    
    product = Product.objects.filter(id=product_id, is_delete=False).first()
    
    if not product:
        return render(request, 'guest/product_not_found.html')
    
    # Get stock info
    stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
    stock_available = stock.can_order_stock if stock else 0
    
    # Get related products
    related_products = Product.objects.filter(
        goods_class=product.goods_class,
        is_delete=False
    ).exclude(id=product_id)[:4]
    
    context = {
        'product': product,
        'stock_available': stock_available,
        'related_products': related_products,
    }
    
    return render(request, 'guest/product_detail.html', context)


def view_services(request):
    """View available services"""
    services = [
        {
            'name': 'Rental Equipment',
            'icon': 'fas fa-key',
            'description': 'Rent equipment for your business needs',
            'features': ['Flexible rental periods', 'Quality equipment', 'Affordable rates']
        },
        {
            'name': 'Storage Units',
            'icon': 'fas fa-warehouse',
            'description': 'Secure storage solutions for your goods',
            'features': ['24/7 security', 'Climate controlled', 'Various sizes']
        },
        {
            'name': 'Smart Lockers',
            'icon': 'fas fa-lock',
            'description': 'Convenient locker services',
            'features': ['Digital access', 'Secure storage', 'Easy pickup']
        },
        {
            'name': 'Marketplace',
            'icon': 'fas fa-shopping-cart',
            'description': 'Buy products from our marketplace',
            'features': ['Wide selection', 'Competitive prices', 'Fast delivery']
        }
    ]
    
    context = {
        'services': services,
    }
    
    return render(request, 'guest/services.html', context)


def pricing_page(request):
    """View pricing information"""
    pricing_plans = [
        {
            'name': 'Basic',
            'price': '₹999',
            'period': 'month',
            'features': [
                '10 Products',
                'Basic Support',
                'Email Notifications',
                'Standard Shipping'
            ]
        },
        {
            'name': 'Professional',
            'price': '₹2,999',
            'period': 'month',
            'features': [
                '50 Products',
                'Priority Support',
                'SMS & Email Notifications',
                'Express Shipping',
                'Storage Discount'
            ],
            'popular': True
        },
        {
            'name': 'Enterprise',
            'price': '₹9,999',
            'period': 'month',
            'features': [
                'Unlimited Products',
                '24/7 Dedicated Support',
                'All Notifications',
                'Free Shipping',
                'Premium Storage',
                'Custom Solutions'
            ]
        }
    ]
    
    context = {
        'pricing_plans': pricing_plans,
    }
    
    return render(request, 'guest/pricing.html', context)


def contact_page(request):
    """Contact page"""
    context = {
        'company_name': 'MultiStock Logistics',
        'email': 'support@multistock.com',
        'phone': '+91 1234567890',
        'address': 'Mumbai, Maharashtra, India'
    }
    
    return render(request, 'guest/contact.html', context)


def guest_rentals(request):
    """View rentals as guest (view-only) with pagination"""
    from rentals.models import RentalItem, RentalCategory
    from django.core.paginator import Paginator
    
    items_qs = RentalItem.objects.filter(status='available').select_related('category').order_by('-created_at')
    categories = RentalCategory.objects.all()
    total_items = items_qs.count()
    
    paginator = Paginator(items_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Process items to ensure images are accessible (safe for templates)
    items_with_images = []
    for item in page_obj.object_list:
        item.display_image = None
        # Primary: rental item's own image
        if item.image:
            url = getattr(item.image, 'url', None)
            item.display_image = url or f'/media/{item.image}'
        # Fallback: category image if rental image missing
        elif hasattr(item, 'category') and getattr(item.category, 'image', None):
            cat_img = item.category.image
            url = getattr(cat_img, 'url', None)
            item.display_image = url or f'/media/{cat_img}'
        items_with_images.append(item)
    
    context = {
        'items': items_with_images,
        'page_obj': page_obj,
        'categories': categories,
        'is_guest': True,
        'total_items': total_items,
    }
    
    return render(request, 'guest/rentals.html', context)


def guest_storage(request):
    """View storage units as guest (view-only) with pagination"""
    from storage.models import StorageUnit
    from django.core.paginator import Paginator
    
    units_qs = StorageUnit.objects.filter(status='available').order_by('unit_number')
    total_units = StorageUnit.objects.count()
    available_units = StorageUnit.objects.filter(status='available').count()
    occupied_units = StorageUnit.objects.filter(status='occupied').count()
    maintenance_units = StorageUnit.objects.filter(status='maintenance').count()
    
    paginator = Paginator(units_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    units_with_info = []
    for unit in page_obj.object_list:
        unit.image_url = None
        if hasattr(unit, 'image') and unit.image:
            try:
                unit.image_url = unit.image.url if hasattr(unit.image, 'url') else f'/media/{unit.image}'
            except Exception:
                pass
        units_with_info.append(unit)
    
    context = {
        'units': units_with_info,
        'page_obj': page_obj,
        'total_units': total_units,
        'available_units': available_units,
        'occupied_units': occupied_units,
        'maintenance_units': maintenance_units,
        'is_guest': True,
    }
    
    return render(request, 'guest/storage.html', context)


def guest_lockers(request):
    """View lockers as guest (view-only) with pagination"""
    from lockers.models import Locker, LockerType
    from django.core.paginator import Paginator
    
    lockers_qs = Locker.objects.filter(status='available').select_related('locker_type').order_by('locker_number')
    locker_types = LockerType.objects.all()
    total_lockers = Locker.objects.count()
    available = Locker.objects.filter(status='available').count()
    occupied = Locker.objects.filter(status='occupied').count()
    maintenance = Locker.objects.filter(status='maintenance').count()
    
    paginator = Paginator(lockers_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    lockers_with_info = []
    for locker in page_obj.object_list:
        locker.image_url = None
        if hasattr(locker, 'image') and locker.image:
            try:
                locker.image_url = locker.image.url if hasattr(locker.image, 'url') else f'/media/{locker.image}'
            except Exception:
                pass
        lockers_with_info.append(locker)
    
    context = {
        'lockers': lockers_with_info,
        'page_obj': page_obj,
        'locker_types': locker_types,
        'total_lockers': total_lockers,
        'available': available,
        'occupied': occupied,
        'maintenance': maintenance,
        'is_guest': True,
    }
    
    return render(request, 'guest/lockers.html', context)