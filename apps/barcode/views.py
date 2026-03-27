from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from goods.models import ListModel as Product
import io, base64

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

try:
    import barcode as python_barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False


@login_required
def barcode_system(request):
    return render(request, 'barcode/barcode_system.html')

@login_required
def barcode_scanner(request):
    return render(request, 'barcode/barcode_system.html')

@login_required
def barcode_generator(request):
    return render(request, 'barcode/barcode_system.html')


@login_required
def generate_product_barcode(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_delete=False)
    barcode_b64 = qr_b64 = None

    if BARCODE_AVAILABLE:
        try:
            Code128 = python_barcode.get_barcode_class('code128')
            buf = io.BytesIO()
            Code128(product.goods_code, writer=ImageWriter()).write(buf)
            buf.seek(0)
            barcode_b64 = base64.b64encode(buf.read()).decode()
        except Exception:
            pass

    if QR_AVAILABLE:
        try:
            qr_data = f"SKU:{product.goods_code}\nName:{product.goods_desc}\nPrice:{product.goods_price}"
            img = qrcode.make(qr_data)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            qr_b64 = base64.b64encode(buf.read()).decode()
        except Exception:
            pass

    return render(request, 'barcode/product_barcode.html', {
        'product': product, 'barcode_b64': barcode_b64, 'qr_b64': qr_b64,
    })


@login_required
def generate_qr_api(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_delete=False)
    if not QR_AVAILABLE:
        return JsonResponse({'success': False, 'message': 'qrcode not installed'})
    try:
        img = qrcode.make(f"SKU:{product.goods_code}|{product.goods_desc}|{product.goods_price}")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return JsonResponse({'success': True, 'qr': base64.b64encode(buf.read()).decode(), 'sku': product.goods_code})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
