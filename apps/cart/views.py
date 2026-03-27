from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import Cart, CartItem, Coupon
from goods.models import ListModel
from stock.models import StockListModel
import json
import logging

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = [{
        'id': item.id,
        'product_id': item.product.id if item.product else None,
        'title': item.product_name,
        'price': float(item.unit_price),
        'quantity': item.quantity,
        'total': float(item.total_price),
        'seller': item.seller,
        'image': item.image_url
    } for item in cart.items.all()]
    
    return JsonResponse({
        'items': items,
        'total_items': cart.total_items,
        'subtotal': float(cart.subtotal)
    })

@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        product = None
        
        # Try to find product by ID or goods_code
        if product_id:
            try:
                product = ListModel.objects.filter(id=int(product_id)).first()
            except (ValueError, TypeError):
                product = ListModel.objects.filter(goods_code=product_id).first()
        
        if not product:
            return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
        
        # Validate stock availability
        stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
        if not stock or stock.can_order_stock < quantity:
            available = stock.can_order_stock if stock else 0
            return JsonResponse({
                'success': False,
                'message': f'Only {available} units available in stock'
            }, status=400)
        
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'product_name': data.get('title', product.goods_desc),
                'unit_price': data.get('price', product.goods_price),
                'quantity': quantity,
                'seller': data.get('seller', product.goods_supplier),
                'image_url': data.get('image', '')
            }
        )
        
        if not created:
            new_quantity = item.quantity + quantity
            if stock.can_order_stock < new_quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {stock.can_order_stock} units available. You already have {item.quantity} in cart.'
                }, status=400)
            item.quantity = new_quantity
            item.save()
        
        return JsonResponse({'success': True, 'item_id': item.id})
    
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Failed to add item to cart'}, status=400)

@login_required
@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    data = json.loads(request.body)
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    new_quantity = data.get('quantity', item.quantity)
    
    # Validate stock availability
    if item.product:
        stock = StockListModel.objects.filter(goods_code=item.product.goods_code).first()
        if stock and stock.can_order_stock < new_quantity:
            return JsonResponse({
                'success': False,
                'message': f'Only {stock.can_order_stock} units available'
            }, status=400)
    
    item.quantity = new_quantity
    item.save()
    
    return JsonResponse({'success': True, 'total': float(item.total_price)})

@login_required
@require_http_methods(["DELETE"])
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def clear_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.items.all().delete()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def apply_coupon(request):
    data = json.loads(request.body)
    code = data.get('code', '').upper()
    subtotal = float(data.get('subtotal', 0))
    
    try:
        coupon = Coupon.objects.get(code=code)
        if not coupon.is_valid():
            return JsonResponse({'success': False, 'message': 'Coupon expired or invalid'})
        
        if subtotal < float(coupon.min_order_amount):
            return JsonResponse({'success': False, 'message': f'Minimum order of Rs.{coupon.min_order_amount} required'})
        
        discount = 0
        if coupon.discount_type == 'percentage':
            discount = (subtotal * float(coupon.discount_value)) / 100
        elif coupon.discount_type == 'fixed':
            discount = float(coupon.discount_value)
        
        return JsonResponse({
            'success': True,
            'discount': discount,
            'type': coupon.discount_type,
            'message': 'Coupon applied successfully'
        })
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid coupon code'})

@login_required
def cart_page(request):
    """Display cart page with all items"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    
    context = {
        'cart': cart,
        'items': items,
        'subtotal': cart.subtotal,
        'total_items': cart.total_items,
    }
    return render(request, 'cart/cart.html', context)

@login_required
@require_http_methods(["POST"])
def buy_now(request):
    """Direct purchase with payment (Buy Now)"""
    try:
        data = json.loads(request.body)
        
        product_id = data.get('product_id')
        product_type = data.get('type', 'storage')  # 'storage', 'rental', 'locker', 'product'
        price = float(data.get('price', 0))
        quantity = int(data.get('quantity', 1))
        
        # Validate
        if not product_id or price <= 0:
            return JsonResponse({
                'success': False,
                'message': 'Invalid product information'
            }, status=400)
        
        total_amount = price * quantity
        
        # Create order based on type
        try:
            with transaction.atomic():
                if product_type == 'storage':
                    from apps.storage.models import StorageBooking
                    order = StorageBooking.objects.create(
                        unit_id=product_id,
                        customer=request.user,
                        total_amount=total_amount,
                        status='pending_payment'
                    )
                    order_ref = f"SB{order.id:05d}"
                    
                elif product_type == 'rental':
                    from apps.rentals.models import RentalBooking
                    order = RentalBooking.objects.create(
                        item_id=product_id,
                        customer=request.user,
                        total_amount=total_amount,
                        status='pending_payment'
                    )
                    order_ref = f"RB{order.id:05d}"
                    
                elif product_type == 'locker':
                    from apps.lockers.models import LockerBooking
                    order = LockerBooking.objects.create(
                        locker_id=product_id,
                        customer=request.user,
                        total_amount=total_amount,
                        status='pending_payment'
                    )
                    order_ref = f"LB{order.id:05d}"
                    
                else:  # Regular product
                    order = None
                    order_ref = None
            
            return JsonResponse({
                'success': True,
                'message': 'Order created successfully',
                'order_id': order.id if order else None,
                'order_reference': order_ref,
                'amount': total_amount,
                'redirect_url': '/checkout/payment/' if order else '/checkout/'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error creating order: {str(e)}'
            }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@login_required
@require_http_methods(["POST"])
def checkout_payment(request):
    """Process payment for Buy Now orders"""
    try:
        data = json.loads(request.body)
        
        order_id = data.get('order_id')
        order_type = data.get('type', 'storage')
        payment_method = data.get('payment_method', 'online')
        
        # Get and update order with ownership validation
        order = None
        try:
            if order_type == 'storage':
                from apps.storage.models import StorageBooking
                order = StorageBooking.objects.get(id=order_id, customer_email=request.user.email)
            elif order_type == 'rental':
                from apps.rentals.models import RentalBooking
                order = RentalBooking.objects.get(id=order_id, customer_email=request.user.email)
            elif order_type == 'locker':
                from apps.lockers.models import LockerBooking
                order = LockerBooking.objects.get(id=order_id, customer_email=request.user.email)
        except:
            pass
        
        if not order:
            return JsonResponse({
                'success': False,
                'message': 'Order not found'
            }, status=404)
        
        # Update order status
        with transaction.atomic():
            if payment_method == 'online':
                order.status = 'payment_pending'
                order.payment_method = 'online'
            elif payment_method == 'cash':
                order.status = 'confirmed'
                order.payment_method = 'cash_on_delivery'
            
            order.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Order confirmed',
            'order_id': order.id,
            'status': order.status,
            'redirect_url': f'/orders/{order.id}/'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
