from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from stock.models import StockListModel as Stock
import csv
import io

@login_required
def bulk_upload_stock_api(request):
    if request.method == 'POST':
        try:
            if 'file' not in request.FILES:
                return JsonResponse({'success': False, 'message': 'No file uploaded'}, status=400)
            
            file = request.FILES['file']
            
            # Read CSV file
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            count = 0
            errors = []
            
            for row in reader:
                try:
                    goods_code = row.get('goods_code', '').strip()
                    goods_desc = row.get('goods_desc', '').strip()
                    
                    if not goods_code or not goods_desc:
                        continue
                    
                    onhand = int(row.get('onhand_stock', 0))
                    available = int(row.get('can_order_stock', 0))
                    supplier = row.get('supplier', '').strip()
                    
                    # Check if stock exists
                    stock = Stock.objects.filter(goods_code=goods_code).first()
                    
                    if stock:
                        # Update existing
                        stock.goods_desc = goods_desc
                        stock.goods_qty = onhand
                        stock.onhand_stock = onhand
                        stock.can_order_stock = available
                        if supplier:
                            stock.supplier = supplier
                        stock.save()
                    else:
                        # Create new
                        Stock.objects.create(
                            goods_code=goods_code,
                            goods_desc=goods_desc,
                            goods_qty=onhand,
                            onhand_stock=onhand,
                            can_order_stock=available,
                            ordered_stock=0,
                            damage_stock=0,
                            supplier=supplier or '',
                            openid=request.user.username
                        )
                    
                    count += 1
                except Exception as e:
                    errors.append(f"Row with code {row.get('goods_code', 'unknown')}: {str(e)}")
            
            if errors:
                return JsonResponse({
                    'success': True,
                    'count': count,
                    'message': f'Uploaded {count} items with {len(errors)} errors',
                    'errors': errors
                })
            
            return JsonResponse({'success': True, 'count': count})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'POST required'}, status=405)
