from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Coupon
from django.views.decorators.http import require_http_methods
import json

from permissions.decorators import require_role

@login_required
@require_role('superadmin', 'admin')
def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'coupons/list.html', {'coupons': coupons})

@login_required
@require_role('superadmin', 'admin')
def coupon_create(request):
    if request.method == 'POST':
        try:
            Coupon.objects.create(
                code=request.POST['code'].upper(),
                description=request.POST.get('description', ''),
                discount_type=request.POST['discount_type'],
                discount_value=request.POST['discount_value'],
                min_amount=request.POST.get('min_amount', 0),
                max_discount=request.POST.get('max_discount') or None,
                applicable_to=request.POST['applicable_to'],
                usage_limit=request.POST.get('usage_limit') or None,
                valid_from=request.POST['valid_from'],
                valid_until=request.POST['valid_until'],
                is_active=request.POST.get('is_active') == 'on',
                created_by=request.user
            )
            messages.success(request, 'Coupon created successfully')
            return redirect('coupons:list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'coupons/form.html')

@login_required
@require_role('superadmin', 'admin')
def coupon_edit(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    
    if request.method == 'POST':
        try:
            coupon.code = request.POST['code'].upper()
            coupon.description = request.POST.get('description', '')
            coupon.discount_type = request.POST['discount_type']
            coupon.discount_value = request.POST['discount_value']
            coupon.min_amount = request.POST.get('min_amount', 0)
            coupon.max_discount = request.POST.get('max_discount') or None
            coupon.applicable_to = request.POST['applicable_to']
            coupon.usage_limit = request.POST.get('usage_limit') or None
            coupon.valid_from = request.POST['valid_from']
            coupon.valid_until = request.POST['valid_until']
            coupon.is_active = request.POST.get('is_active') == 'on'
            coupon.save()
            messages.success(request, 'Coupon updated successfully')
            return redirect('coupons:list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'coupons/form.html', {'coupon': coupon})

@login_required
@require_role('superadmin', 'admin')
def coupon_delete(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully')
    return redirect('coupons:list')

@require_http_methods(["POST"])
def validate_coupon(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '').upper()
        amount = float(data.get('amount', 0))
        service_type = data.get('service_type', 'all')
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return JsonResponse({'valid': False, 'message': 'Invalid coupon code'})
        
        is_valid, message = coupon.is_valid()
        if not is_valid:
            return JsonResponse({'valid': False, 'message': message})
        
        if coupon.applicable_to not in ['all', service_type]:
            return JsonResponse({'valid': False, 'message': f'Coupon not applicable to {service_type}'})
        
        if amount < coupon.min_amount:
            return JsonResponse({'valid': False, 'message': f'Minimum amount ₹{coupon.min_amount} required'})
        
        discount = coupon.calculate_discount(amount)
        
        return JsonResponse({
            'valid': True,
            'discount': float(discount),
            'code': coupon.code,
            'message': 'Coupon applied successfully'
        })
    except Exception as e:
        return JsonResponse({'valid': False, 'message': str(e)})

@require_http_methods(["POST"])
def apply_coupon(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '').upper()
        
        coupon = get_object_or_404(Coupon, code=code)
        coupon.usage_count += 1
        coupon.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
