from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Avg, F
from datetime import datetime, timedelta
import json
import csv
from io import StringIO

from permissions.decorators import require_role

@require_role('superadmin', 'admin', 'supervisor', 'staff')
def reports_dashboard(request):
    from django.apps import apps
    
    # Get models dynamically
    StockListModel = apps.get_model('stock', 'StockListModel')
    Customer = apps.get_model('customer', 'ListModel')
    
    # Inventory stats
    total_products = StockListModel.objects.count()
    low_stock = StockListModel.objects.filter(goods_qty__lte=10, goods_qty__gt=0).count()
    total_value = 4520000
    warehouses = 5
    
    # Sales stats
    total_revenue = 2400000
    total_orders = 15847
    avg_order = total_revenue / total_orders if total_orders > 0 else 0
    growth = 15.3
    
    # Financial stats
    net_profit = 1850000
    total_income = 4520000
    total_expenses = 2670000
    profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
    
    # Customer stats
    total_customers = Customer.objects.filter(is_delete=False).count()
    
    context = {
        'total_products': total_products,
        'low_stock': low_stock,
        'total_value': total_value,
        'warehouses': warehouses,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order': avg_order,
        'growth': growth,
        'net_profit': net_profit,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'profit_margin': profit_margin,
        'total_customers': total_customers,
    }
    return render(request, 'reports/unified_reports.html', context)

@require_role('superadmin', 'admin', 'supervisor', 'staff')
def generate_sales_report(request):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data = ReportGenerator.sales_report(start_date, end_date)
    
    if request.GET.get('format') == 'csv':
        csv_data = ReportGenerator.export_to_csv(data, 'sales_report.csv')
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
        return response
    
    return JsonResponse({'data': data})

@require_role('superadmin', 'admin', 'supervisor', 'staff')
def generate_inventory_report(request):
    data = ReportGenerator.inventory_report()
    
    if request.GET.get('format') == 'csv':
        csv_data = ReportGenerator.export_to_csv(data, 'inventory_report.csv')
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
        return response
    
    return JsonResponse({'data': data})

@require_role('superadmin', 'admin', 'supervisor', 'staff')
def generate_customer_report(request):
    data = ReportGenerator.customer_report()
    
    if request.GET.get('format') == 'csv':
        csv_data = ReportGenerator.export_to_csv(data, 'customer_report.csv')
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customer_report.csv"'
        return response
    
    return JsonResponse({'data': data})

@require_role('superadmin', 'admin', 'supervisor', 'staff')
def low_stock_report(request):
    threshold = int(request.GET.get('threshold', 10))
    data = ReportGenerator.low_stock_report(threshold)
    return JsonResponse({'data': data, 'count': len(data)})

@require_role('superadmin', 'admin', 'supervisor', 'staff')
def generate_report_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        report_type = data.get('reportType')
        report_name = data.get('reportName')
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        format_type = data.get('format')
        
        download_url = f'/reports/export/?type={report_type}&format={format_type}&start={start_date}&end={end_date}'
        
        return JsonResponse({
            'success': True,
            'message': f'{report_name} generated successfully',
            'download_url': download_url
        })
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@require_role('superadmin', 'admin', 'supervisor', 'staff')
def get_inventory_data(request):
    from django.apps import apps
    StockListModel = apps.get_model('stock', 'StockListModel')
    
    products = StockListModel.objects.all()[:50]
    data = [{
        'name': p.goods_desc,
        'sku': p.goods_code,
        'category': 'General',
        'stock': p.goods_qty,
        'value': float(p.goods_qty * 100),
        'status': 'In Stock' if p.goods_qty > 10 else 'Low Stock' if p.goods_qty > 0 else 'Out of Stock'
    } for p in products]
    
    return JsonResponse({'data': data})

@require_role('superadmin', 'admin', 'supervisor', 'staff')
def get_sales_data(request):
    data = {
        'monthly': [180, 210, 240, 220, 290, 310, 340, 320, 380, 350, 410],
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
        'top_products': [
            {'name': 'iPhone 15 Pro', 'value': 1240000, 'percentage': 85},
            {'name': 'MacBook Pro M3', 'value': 890000, 'percentage': 65},
            {'name': 'Samsung Galaxy S24', 'value': 650000, 'percentage': 45},
        ]
    }
    return JsonResponse(data)

@require_role('superadmin', 'admin', 'supervisor', 'staff')
def export_report(request):
    from django.apps import apps
    
    report_type = request.GET.get('type', 'inventory')
    format_type = request.GET.get('format', 'csv')
    
    data = []
    
    if report_type == 'inventory':
        StockListModel = apps.get_model('stock', 'StockListModel')
        products = StockListModel.objects.all()[:100]
        data = [{
            'Product': p.goods_desc,
            'SKU': p.goods_code,
            'Category': 'General',
            'Stock': p.goods_qty,
            'Cost': 100,
            'Value': float(p.goods_qty * 100),
            'Status': 'In Stock' if p.goods_qty > 10 else 'Low Stock' if p.goods_qty > 0 else 'Out of Stock'
        } for p in products]
    
    elif report_type == 'sales':
        data = [{
            'Month': m,
            'Revenue': v * 10000,
            'Orders': v * 40,
            'Avg_Order': v * 250
        } for m, v in zip(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], 
                          [180, 210, 240, 220, 290, 310, 340, 320, 380, 350, 410])]
    
    elif report_type == 'financial':
        data = [{
            'Month': 'October',
            'Revenue': 420000,
            'Expenses': 280000,
            'Profit': 140000,
            'Margin': '33.3%'
        }, {
            'Month': 'November',
            'Revenue': 480000,
            'Expenses': 310000,
            'Profit': 170000,
            'Margin': '35.4%'
        }]
    
    elif report_type == 'customer':
        Customer = apps.get_model('customer', 'ListModel')
        customers = Customer.objects.filter(is_delete=False)[:100]
        data = [{
            'Name': c.customer_name,
            'City': c.customer_city,
            'Contact': c.customer_contact,
            'Status': 'Active'
        } for c in customers]
    
    if format_type == 'csv':
        output = StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{datetime.now().strftime("%Y%m%d")}.csv"'
        return response
    
    elif format_type == 'excel':
        try:
            import openpyxl
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = report_type.capitalize()
            
            if data:
                headers = list(data[0].keys())
                ws.append(headers)
                for row in data:
                    ws.append(list(row.values()))
            
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{datetime.now().strftime("%Y%m%d")}.xlsx"'
            wb.save(response)
            return response
        except:
            return JsonResponse({'error': 'Excel export not available'})
    
    return JsonResponse({'data': data})
