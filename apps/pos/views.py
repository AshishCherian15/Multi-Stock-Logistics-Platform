from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_http_methods
from goods.models import ListModel
from stock.models import StockListModel, StockMovement
from .models import POSSale, POSSaleItem
from permissions.decorators import require_role
import json

@login_required
@require_role('superadmin', 'admin', 'subadmin', 'staff')
def pos_interface(request):
    products = []
    for product in ListModel.objects.filter(is_delete=False):
        stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
        if stock and stock.can_order_stock > 0:
            products.append({
                'id': product.id,
                'name': product.goods_desc,
                'code': product.goods_code,
                'price': float(product.goods_price or 0),
                'stock': int(stock.can_order_stock),
                'category': product.goods_class or 'General'
            })
    
    return render(request, 'pos/interface.html', {'products': json.dumps(products)})

@login_required
@require_role('superadmin', 'admin', 'subadmin', 'staff')
@require_http_methods(["POST"])
def complete_sale(request):
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        payment_method = data.get('payment_method', 'cash')
        
        if not items:
            return JsonResponse({'success': False, 'error': 'No items in sale'}, status=400)
        
        with transaction.atomic():
            for item in items:
                stock = StockListModel.objects.select_for_update().filter(goods_code=item['code']).first()
                if not stock or stock.can_order_stock < item['quantity']:
                    return JsonResponse({
                        'success': False,
                        'error': f'Insufficient stock for {item["name"]}'
                    }, status=400)
            
            total_amount = sum(item['price'] * item['quantity'] for item in items)
            sale = POSSale.objects.create(
                sale_number=f'POS-{POSSale.objects.count() + 1:06d}',
                total_amount=total_amount,
                payment_method=payment_method,
                cashier=request.user
            )
            
            for item in items:
                product = ListModel.objects.get(goods_code=item['code'])
                POSSaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=item['quantity'],
                    unit_price=item['price'],
                    total_price=item['price'] * item['quantity']
                )
                
                stock = StockListModel.objects.select_for_update().get(goods_code=item['code'])
                stock.onhand_stock -= item['quantity']
                stock.save()
                
                StockMovement.objects.create(
                    goods_code=item['code'],
                    movement_type='out',
                    quantity=-item['quantity'],
                    reason=f'POS Sale {sale.sale_number}',
                    user=request.user
                )
            
            # Create invoice in billing system
            from billing.models import Invoice, InvoiceItem
            from datetime import date, timedelta
            
            invoice = Invoice.objects.create(
                invoice_number=sale.sale_number,
                invoice_type='product',
                customer_name='Walk-in Customer',
                customer_email='',
                customer_phone='',
                customer_address='',
                due_date=date.today(),
                subtotal=total_amount,
                grand_total=total_amount,
                payment_method=payment_method,
                status='paid',
                created_by=request.user
            )
            
            for item in items:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item['name'],
                    quantity=item['quantity'],
                    price=item['price'],
                    amount=item['price'] * item['quantity']
                )
            
            return JsonResponse({
                'success': True,
                'sale_number': sale.sale_number,
                'sale_id': sale.id,
                'total': float(total_amount)
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_role('superadmin', 'admin', 'subadmin', 'staff')
def pos_sales(request):
    sales = POSSale.objects.select_related('cashier').prefetch_related('items__product').order_by('-created_at')[:50]
    return render(request, 'pos/sales.html', {'sales': sales})

@login_required
@require_role('superadmin', 'admin', 'subadmin', 'staff')
def bill_view(request, sale_id):
    sale = POSSale.objects.prefetch_related('items__product').get(id=sale_id)
    return render(request, 'pos/bill.html', {'sale': sale})

@login_required
@require_role('superadmin', 'admin', 'subadmin', 'staff')
def bill_pdf(request, sale_id):
    from django.http import HttpResponse
    
    sale = POSSale.objects.prefetch_related('items__product').get(id=sale_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{sale.sale_number}.pdf"'
    response.write(b'%PDF-1.4\n')
    response.write(f'Bill #{sale.sale_number}\nTotal: Rs.{sale.total_amount}'.encode())
    return response
