from django.db import connection
from datetime import datetime, timedelta
import csv
from io import StringIO

class ReportGenerator:
    
    @staticmethod
    def sales_report(start_date, end_date):
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as orders,
                    SUM(total_amount) as revenue,
                    AVG(total_amount) as avg_order
                FROM orders_order
                WHERE created_at BETWEEN ? AND ?
                AND order_type = 'sale'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            ''', [start_date, end_date])
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def inventory_report():
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    goods_code,
                    goods_qty as quantity,
                    can_order_stock as available,
                    ordered_stock as ordered
                FROM stock_stocklistmodel
                ORDER BY goods_qty ASC
                LIMIT 100
            ''')
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def customer_report():
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    c.customer_name,
                    c.customer_email,
                    COUNT(o.id) as total_orders,
                    COALESCE(SUM(o.total_amount), 0) as total_spent
                FROM customer_listmodel c
                LEFT JOIN orders_order o ON c.id = o.customer_id
                WHERE c.is_delete = 0
                GROUP BY c.id
                ORDER BY total_spent DESC
                LIMIT 50
            ''')
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def export_to_csv(data, filename):
        if not data:
            return None
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    @staticmethod
    def low_stock_report(threshold=10):
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT goods_code, goods_qty
                FROM stock_stocklistmodel
                WHERE goods_qty < ?
                ORDER BY goods_qty ASC
            ''', [threshold])
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
