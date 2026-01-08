from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Wishlist, WishlistItem
from goods.models import ListModel
import json

@login_required
@require_http_methods(["GET"])
def get_wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    items = [{
        'id': item.id,
        'product_id': item.product.id if item.product else None,
        'title': item.product_name,
        'price': float(item.price),
        'description': item.description,
        'seller': item.seller,
        'image': item.image_url
    } for item in wishlist.items.all()]
    
    return JsonResponse({'items': items})

@login_required
@require_http_methods(["POST"])
def add_to_wishlist(request):
    data = json.loads(request.body)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    product_id = data.get('product_id')
    product = ListModel.objects.filter(id=product_id).first() if product_id else None
    
    item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product,
        defaults={
            'product_name': data.get('title'),
            'price': data.get('price'),
            'description': data.get('description', ''),
            'seller': data.get('seller', ''),
            'image_url': data.get('image', '')
        }
    )
    
    return JsonResponse({'success': True, 'created': created})

@login_required
@require_http_methods(["DELETE"])
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    item.delete()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def clear_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user).first()
    if wishlist:
        wishlist.items.all().delete()
    return JsonResponse({'success': True})

@login_required
def wishlist_page(request):
    """Display wishlist page with all items"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product').all()
    
    context = {
        'wishlist': wishlist,
        'items': items,
        'total_items': items.count(),
    }
    return render(request, 'wishlist/wishlist.html', context)
