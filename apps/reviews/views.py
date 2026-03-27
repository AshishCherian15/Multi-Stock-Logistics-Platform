from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from goods.models import ListModel as Product
from .models import Review
import json

@login_required
@require_http_methods(["POST"])
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST
    rating = int(data.get('rating', 0))
    if not 1 <= rating <= 5:
        return JsonResponse({'success': False, 'message': 'Rating must be 1–5.'})
    from orders.models import Order
    is_verified = Order.objects.filter(customer_user=request.user, items__product=product, status='delivered').exists()
    review, created = Review.objects.update_or_create(
        product=product, user=request.user,
        defaults={'rating': rating, 'title': data.get('title',''), 'body': data.get('body',''), 'is_verified_purchase': is_verified}
    )
    return JsonResponse({'success': True, 'created': created})

def product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).select_related('user')
    from django.db.models import Avg
    avg = reviews.aggregate(avg=Avg('rating'))['avg']
    return render(request, 'reviews/list.html', {'product': product, 'reviews': reviews, 'average_rating': round(avg or 0, 1)})

@login_required
@require_http_methods(["POST"])
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return JsonResponse({'success': True})
