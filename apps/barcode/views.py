from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from goods.models import ListModel as Product
import io
import base64

@login_required
def barcode_scanner(request):
    return render(request, 'barcode/barcode_system.html')

@login_required
def barcode_generator(request):
    return render(request, 'barcode/barcode_system.html')

@login_required
def barcode_system(request):
    return render(request, 'barcode/barcode_system.html')

@login_required
def generate_product_barcode(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id, is_delete=False)
        
        # Generate simple barcode HTML page
        barcode_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Barcode - {product.goods_desc}</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .barcode-container {{ border: 2px solid #000; padding: 20px; display: inline-block; }}
                .barcode {{ font-family: 'Courier New', monospace; font-size: 24px; letter-spacing: 2px; }}
                .product-info {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="barcode-container">
                <h2>Product Barcode</h2>
                <div class="product-info">
                    <strong>{product.goods_desc}</strong><br>
                    SKU: {product.goods_code}<br>
                    Price: ₹{product.goods_price}
                </div>
                <div class="barcode">||||| {product.goods_code} |||||</div>
                <p><small>Scan this barcode for product identification</small></p>
            </div>
            <br><br>
            <button onclick="window.print()">Print Barcode</button>
            <button onclick="window.close()">Close</button>
        </body>
        </html>
        '''
        
        return HttpResponse(barcode_html, content_type='text/html')
        
    except Exception as e:
        return HttpResponse(f'Error generating barcode: {str(e)}', status=400)