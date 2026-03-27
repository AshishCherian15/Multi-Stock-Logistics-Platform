"""
Guest Access Views - Redesigned with Animated Landing Page
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from permissions.decorators import get_user_role


def home(request):
    """Landing page - handles guest mode entry"""
    
    # Check if user clicked "Continue as Guest"
    if request.GET.get('guest_mode') == 'true':
        request.session['guest_mode'] = True
        request.session['is_guest'] = True
        request.session.modified = True
        return redirect('/guest/dashboard/')
    
    # Otherwise, show login selection page
    return render(request, 'auth/login_selection.html')


def guest_dashboard(request):
    """
    Guest landing page with animated stat cards
    Shows: Marketplace, Auctions, Forums, About cards
    """
    # If not in guest mode yet, set it now (allows direct access)
    if not request.session.get('guest_mode', False):
        request.session['guest_mode'] = True
        request.session['is_guest'] = True
        request.session.modified = True
    
    # Redirect authenticated users
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    # Get counts for stat cards
    # try:
    #     from multistock.models import Listing, Auction, Forum
    #     marketplace_count = Listing.objects.filter(is_active=True).count()
    #     auction_count = Auction.objects.filter(is_active=True).count()
    #     forum_count = Forum.objects.count()
    # except Exception as e:
    marketplace_count = 0
    auction_count = 0
    forum_count = 0
    
    return render(request, 'guest/dashboard.html', {
        'is_guest': True,
        'guest_mode_active': True,
        'stats': {
            'marketplace': marketplace_count,
            'auctions': auction_count,
            'forums': forum_count,
        }
    })


def guest_marketplace(request):
    """Guest marketplace page - shows real products from database"""
    # If not in guest mode yet, set it now
    if not request.session.get('guest_mode', False):
        request.session['guest_mode'] = True
        request.session['is_guest'] = True
        request.session.modified = True
    
    # Redirect authenticated users to products page
    if request.user.is_authenticated:
        return redirect('/products/')
    
    # Get real products from database
    from goods.models import ListModel as Product
    from stock.models import StockListModel
    
    products_qs = Product.objects.filter(is_delete=False).order_by('-create_time')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Attach stock information and images for current page
    products_with_stock = []
    for product in page_obj.object_list:
        stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
        product.stock_qty = stock.goods_qty if stock else 0
        product.stock_available = stock.can_order_stock if stock else 0
        product.stock_image = None
        if stock and stock.goods_image:
            try:
                product.stock_image = stock.goods_image.url if hasattr(stock.goods_image, 'url') else f'/media/{stock.goods_image}'
            except Exception:
                pass
        products_with_stock.append(product)
    
    # Get categories for filters
    categories = Product.objects.filter(is_delete=False).exclude(goods_class__isnull=True).exclude(goods_class='').values_list('goods_class', flat=True).distinct()
    
    return render(request, 'guest/marketplace.html', {
        'products': products_with_stock,
        'page_obj': page_obj,
        'categories': categories,
        'total_products': products_qs.count(),
        'is_guest': True,
        'guest_mode_active': True,
    })


def guest_auctions(request):
    """Guest auctions page - matches uploaded image design"""
    # If not in guest mode yet, set it now
    if not request.session.get('guest_mode', False):
        request.session['guest_mode'] = True
        request.session['is_guest'] = True
        request.session.modified = True
    
    if request.user.is_authenticated:
        return redirect('/multistock/auctions/')
    
    # try:
    #     from multistock.models import Auction
    #     auctions = Auction.objects.filter(is_active=True)[:20]
    #     total_count = Auction.objects.filter(is_active=True).count()
    # except Exception as e:
    auctions = []
    total_count = 0
    
    # Categories for browse section
    categories = [
        {'name': 'Electronics', 'icon': 'fa-laptop'},
        {'name': 'Fashion', 'icon': 'fa-shirt'},
        {'name': 'Home & Garden', 'icon': 'fa-home'},
        {'name': 'Sports', 'icon': 'fa-basketball-ball'},
        {'name': 'Collectibles', 'icon': 'fa-gem'},
        {'name': 'Automotive', 'icon': 'fa-car'},
    ]
    
    return render(request, 'guest/auctions.html', {
        'auctions': auctions,
        'categories': categories,
        'is_guest': True,
        'guest_mode_active': True,
        'total_count': total_count
    })


def guest_forums(request):
    """Forums page - redirect to actual forums"""
    return redirect('/forums/')


def guest_about(request):
    """Guest about page"""
    # Gather live stats
    try:
        from django.contrib.auth.models import User
        from goods.models import ListModel as Product
        from orders.models import Order
        
        total_users = User.objects.count()
        total_products = Product.objects.filter(is_delete=False).count()
        total_transactions = Order.objects.count()
    except Exception:
        total_users = 0
        total_products = 0
        total_transactions = 0
    
    return render(request, 'guest/about.html', {
        'is_guest': request.session.get('guest_mode', False),
        'guest_mode_active': request.session.get('guest_mode', False),
        'stats': {
            'users': total_users,
            'products': total_products,
            'transactions': total_transactions,
            'uptime': '99.9%'  # Static until monitored uptime source added
        }
    })


def exit_guest_mode(request):
    """Exit guest mode and return to login selection"""
    if 'guest_mode' in request.session:
        del request.session['guest_mode']
    return redirect('/')
