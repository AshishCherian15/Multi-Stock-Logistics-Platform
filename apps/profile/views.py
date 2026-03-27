"""
User Profile Views with Real Data
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from permissions.decorators import get_user_role
from goods.models import ListModel as Product
from orders.models import Order
from customer.models import ListModel as Customer


@login_required
def user_profile(request):
    """User profile page with real database data"""
    
    user = request.user
    user_role = get_user_role(user)
    
    # Get user statistics based on role
    if user_role in ['superadmin', 'admin']:
        # Admin statistics
        total_products = Product.objects.filter(is_delete=False).count()
        total_orders = Order.objects.count()
        total_customers = Customer.objects.filter(is_delete=False).count()
        
        stats = {
            'products': total_products,
            'orders': total_orders,
            'customers': total_customers
        }
    elif hasattr(user, 'seller_profile'):
        # Seller statistics
        seller_profile = user.seller_profile
        stats = {
            'total_listings': seller_profile.total_listings,
            'total_sales': seller_profile.total_sales,
            'lifetime_earnings': seller_profile.lifetime_earnings,
            'rating': seller_profile.rating
        }
    else:
        # Customer statistics
        try:
            total_orders = Order.objects.filter(customer__user=user).count()
            total_spent = Order.objects.filter(
                customer__user=user,
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
        except:
            total_orders = 0
            total_spent = 0
        
        stats = {
            'orders': total_orders,
            'total_spent': total_spent
        }
    
    # User details
    profile_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user_role,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    }
    
    context = {
        'profile': profile_data,
        'stats': stats,
        'user_role': user_role,
    }
    
    # Check if embed mode
    if request.GET.get('embed') == '1':
        return render(request, 'profile/user_profile_embed.html', context)
    
    return render(request, 'profile/user_profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile:user_profile')
    
    return render(request, 'profile/edit_profile.html', {'user': request.user})


@login_required
@require_http_methods(["POST"])
def upload_photo(request):
    """Upload profile photo"""
    if request.method == 'POST':
        try:
            import os
            from django.conf import settings
            import time
            from PIL import Image
            import io
            
            # Import here to avoid circular import
            from django.apps import apps
            UserProfile = apps.get_model('users', 'UserProfile')
            
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Handle file upload
            if request.FILES.get('photo'):
                photo = request.FILES['photo']
                
                # Validate image
                try:
                    img = Image.open(photo)
                    img.verify()
                    photo.seek(0)
                except Exception as e:
                    return JsonResponse({'success': False, 'error': 'Invalid image file'})
                
                # Validate file size (2MB)
                if photo.size > 2 * 1024 * 1024:
                    return JsonResponse({'success': False, 'error': 'File too large. Maximum size is 2MB'})
                
                # Create directory
                photo_dir = os.path.join(settings.MEDIA_ROOT, 'profile_photos')
                os.makedirs(photo_dir, exist_ok=True)
                
                # Generate unique filename
                import uuid
                ext = photo.name.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                    ext = 'jpg'
                unique_filename = f"{request.user.username}_{uuid.uuid4().hex[:8]}.{ext}"
                photo_path = os.path.join(photo_dir, unique_filename)
                
                # Store old avatar URL for deletion
                old_avatar_url = profile.avatar_url
                
                # Save new photo
                with open(photo_path, 'wb+') as f:
                    for chunk in photo.chunks():
                        f.write(chunk)
                
                photo_url = f'/media/profile_photos/{unique_filename}?t={int(time.time())}'
                profile.avatar_url = photo_url
                profile.save()
                
                # Log upload event
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f'Avatar uploaded - User: {request.user.id}, File: {unique_filename}, Size: {photo.size}, Type: {photo.content_type}')
                
                # Delete old photo after successful upload
                if old_avatar_url and old_avatar_url.startswith('/media/profile_photos/'):
                    try:
                        old_filename = old_avatar_url.split('/')[-1].split('?')[0]
                        old_path = os.path.join(photo_dir, old_filename)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                            logger.info(f'Old avatar deleted - User: {request.user.id}, File: {old_filename}')
                    except Exception as e:
                        logger.warning(f'Failed to delete old avatar - User: {request.user.id}, Error: {str(e)}')
                
                return JsonResponse({
                    'success': True, 
                    'photo_url': photo_url,
                    'message': 'Photo uploaded successfully'
                })
            
            # Handle URL upload
            elif request.POST.get('photo_url'):
                import urllib.parse
                import requests
                
                photo_url = request.POST.get('photo_url').strip()
                
                # Validate URL format
                if not photo_url.startswith(('http://', 'https://')):
                    return JsonResponse({'success': False, 'error': 'Invalid URL format'})
                
                # Test if URL is accessible
                try:
                    response = requests.head(photo_url, timeout=5, allow_redirects=True)
                    if response.status_code != 200:
                        return JsonResponse({'success': False, 'error': 'URL not accessible'})
                except:
                    pass  # Continue anyway, might work in browser
                
                profile.avatar_url = photo_url
                profile.save()
                
                return JsonResponse({
                    'success': True, 
                    'photo_url': photo_url,
                    'message': 'Photo URL saved successfully'
                })
            
            return JsonResponse({'success': False, 'error': 'No photo provided'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        user = request.user
        current = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        
        if not user.check_password(current):
            return JsonResponse({'success': False, 'error': 'Current password is incorrect'})
        
        if len(new_pass) < 8:
            return JsonResponse({'success': False, 'error': 'Password must be at least 8 characters'})
        
        user.set_password(new_pass)
        user.save()
        update_session_auth_hash(request, user)
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def wishlist_cart_page(request):
    """Wishlist and cart page"""
    return render(request, 'profile/wishlist_cart.html')
