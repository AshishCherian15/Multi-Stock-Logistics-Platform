from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count
from .models import Review, ReviewHelpful
import json

@login_required
@require_http_methods(["POST"])
def submit_review(request):
    """Submit a new review"""
    try:
        data = json.loads(request.body)
        
        review = Review.objects.create(
            user=request.user,
            review_type=data.get('type'),
            item_id=data.get('item_id'),
            rating=int(data.get('rating')),
            title=data.get('title'),
            comment=data.get('comment'),
            verified_purchase=True  # Can add logic to verify actual purchase
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully',
            'review_id': review.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["POST"])
def mark_helpful(request, review_id):
    """Mark a review as helpful"""
    try:
        review = get_object_or_404(Review, id=review_id)
        
        # Toggle helpful vote
        helpful, created = ReviewHelpful.objects.get_or_create(
            review=review,
            user=request.user
        )
        
        if not created:
            helpful.delete()
            review.helpful_count -= 1
            action = 'removed'
        else:
            review.helpful_count += 1
            action = 'added'
        
        review.save()
        
        return JsonResponse({
            'success': True,
            'action': action,
            'count': review.helpful_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

def get_reviews(request, review_type, item_id):
    """Get all reviews for an item"""
    reviews = Review.objects.filter(
        review_type=review_type,
        item_id=item_id
    ).select_related('user')
    
    # Calculate average rating
    stats = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Get rating distribution
    rating_dist = {}
    for i in range(1, 6):
        rating_dist[i] = reviews.filter(rating=i).count()
    
    reviews_data = [{
        'id': r.id,
        'user': r.user.get_full_name() or r.user.username,
        'rating': r.rating,
        'title': r.title,
        'comment': r.comment,
        'verified': r.verified_purchase,
        'helpful_count': r.helpful_count,
        'created_at': r.created_at.strftime('%B %d, %Y'),
        'star_display': r.star_display
    } for r in reviews]
    
    return JsonResponse({
        'reviews': reviews_data,
        'stats': {
            'average': round(stats['avg_rating'] or 0, 1),
            'total': stats['total_reviews'],
            'distribution': rating_dist
        }
    })

@login_required
def my_reviews(request):
    """View user's own reviews"""
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'reviews/my_reviews.html', {'reviews': reviews})
