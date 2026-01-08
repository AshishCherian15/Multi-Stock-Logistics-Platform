import json
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import time

class AnalyticsStreaming:
    @staticmethod
    def get_realtime_data():
        """Get real-time analytics data"""
        from goods.models import ListModel as Product
        from orders.models import SalesOrder
        from stock.models import StockListModel
        from customer.models import ListModel as Customer
        from django.db.models import Sum, Count
        
        data = {
            'timestamp': timezone.now().isoformat(),
            'total_products': Product.objects.filter(is_delete=False).count(),
            'total_orders': SalesOrder.objects.count(),
            'low_stock_items': StockListModel.objects.filter(goods_qty__lt=10).count(),
            'total_customers': Customer.objects.filter(is_delete=False).count(),
            'orders_today': SalesOrder.objects.filter(created_at__date=timezone.now().date()).count(),
        }
        
        return data
    
    @staticmethod
    def event_stream():
        """Server-Sent Events stream for real-time updates"""
        while True:
            data = AnalyticsStreaming.get_realtime_data()
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(5)  # Update every 5 seconds

@login_required
def realtime_stream(request):
    """SSE endpoint for real-time analytics"""
    response = StreamingHttpResponse(
        AnalyticsStreaming.event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
