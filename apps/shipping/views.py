from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Shipment, Carrier, ShippingRate, TrackingEvent
from permissions.decorators import require_permission
from datetime import datetime, timedelta
import random

@require_permission('shipping', 'view')
def shipments_list(request):
    shipments = Shipment.objects.select_related('carrier', 'order').all()
    
    status = request.GET.get('status')
    carrier_id = request.GET.get('carrier')
    search = request.GET.get('search')
    
    if status:
        shipments = shipments.filter(status=status)
    if carrier_id:
        shipments = shipments.filter(carrier_id=carrier_id)
    if search:
        shipments = shipments.filter(shipment_number__icontains=search) | shipments.filter(tracking_number__icontains=search)
    
    carriers = Carrier.objects.filter(is_active=True)
    
    return render(request, 'shipping/shipments.html', {
        'shipments': shipments[:100],
        'carriers': carriers,
        'selected_status': status,
        'selected_carrier': carrier_id,
        'search': search,
    })

@require_permission('shipping', 'view')
def tracking_detail(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    events = shipment.tracking_events.all()
    return render(request, 'shipping/tracking.html', {'shipment': shipment, 'events': events})

@require_permission('shipping', 'view')
def carriers_list(request):
    carriers = Carrier.objects.all()
    return render(request, 'shipping/carriers.html', {'carriers': carriers})

@require_permission('shipping', 'view')
def rates_list(request):
    rates = ShippingRate.objects.select_related('carrier').filter(is_active=True)
    return render(request, 'shipping/rates.html', {'rates': rates})

def track_shipment_public(request):
    tracking_number = request.GET.get('tracking')
    shipment = None
    events = []
    
    if tracking_number:
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
            events = shipment.tracking_events.all()
        except Shipment.DoesNotExist:
            pass
    
    return render(request, 'shipping/track_public.html', {'shipment': shipment, 'events': events, 'tracking_number': tracking_number})

@require_permission('shipping', 'create')
def create_shipment(request):
    from django.contrib import messages
    if request.method == 'POST':
        shipment = Shipment.objects.create(
            shipment_number=f'SHP{random.randint(100000,999999)}',
            tracking_number=f'TRK{random.randint(100000000,999999999)}',
            carrier_id=request.POST.get('carrier_id'),
            service_type=request.POST.get('service_type'),
            sender_name=request.POST.get('sender_name'),
            sender_address=request.POST.get('sender_address'),
            sender_city=request.POST.get('sender_city'),
            sender_phone=request.POST.get('sender_phone'),
            recipient_name=request.POST.get('recipient_name'),
            recipient_address=request.POST.get('recipient_address'),
            recipient_city=request.POST.get('recipient_city'),
            recipient_phone=request.POST.get('recipient_phone'),
            weight=request.POST.get('weight'),
            shipping_cost=request.POST.get('shipping_cost'),
            total_cost=request.POST.get('total_cost'),
            pickup_date=request.POST.get('pickup_date'),
            estimated_delivery=request.POST.get('estimated_delivery'),
            status='pending'
        )
        messages.success(request, 'Shipment created')
        return redirect('shipments_list')
    return JsonResponse({'success': False}, status=400)

@require_permission('shipping', 'edit')
def update_shipment(request, shipment_id):
    from django.contrib import messages
    shipment = get_object_or_404(Shipment, id=shipment_id)
    if request.method == 'POST':
        shipment.status = request.POST.get('status', shipment.status)
        
        service_type = request.POST.get('service_type', '').strip()
        if service_type:
            shipment.service_type = service_type
        
        weight = request.POST.get('weight', '').strip()
        if weight:
            shipment.weight = weight
        
        shipping_cost = request.POST.get('shipping_cost', '').strip()
        if shipping_cost:
            shipment.shipping_cost = shipping_cost
        
        shipment.save()
        messages.success(request, 'Shipment updated')
        return redirect('shipments_list')
    return JsonResponse({'success': False}, status=400)

@require_permission('shipping', 'delete')
def delete_shipment(request, shipment_id):
    from django.contrib import messages
    shipment = get_object_or_404(Shipment, id=shipment_id)
    shipment.delete()
    messages.success(request, 'Shipment deleted')
    return redirect('shipments_list')

@require_permission('shipping', 'edit')
def add_tracking_event(request, shipment_id):
    from django.contrib import messages
    shipment = get_object_or_404(Shipment, id=shipment_id)
    if request.method == 'POST':
        TrackingEvent.objects.create(
            shipment=shipment,
            status=request.POST.get('status'),
            location=request.POST.get('location'),
            description=request.POST.get('description')
        )
        messages.success(request, 'Tracking event added')
        return redirect('tracking_detail', shipment_id=shipment_id)
    return JsonResponse({'success': False}, status=400)
