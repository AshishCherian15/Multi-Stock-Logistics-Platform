from django.db.models import Q
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class AdvancedSearch:
    @staticmethod
    def search_all(query, user=None):
        """Search across all modules with ranking"""
        if not query:
            return {'results': [], 'count': 0, 'by_category': {}}
        
        cache_key = f'search_{query}_{user.id if user else "anon"}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            results = {
                'products': AdvancedSearch._search_products(query),
                'storage': AdvancedSearch._search_storage(query),
                'rentals': AdvancedSearch._search_rentals(query),
                'orders': AdvancedSearch._search_orders(query, user),
                'customers': AdvancedSearch._search_customers(query),
                'suppliers': AdvancedSearch._search_suppliers(query),
            }
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {'results': [], 'count': 0, 'by_category': {}, 'error': str(e)}
        
        all_results = []
        for category, items in results.items():
            for item in items:
                item['category'] = category
                all_results.append(item)
        
        all_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        response = {
            'results': all_results[:50],
            'count': len(all_results),
            'by_category': {k: len(v) for k, v in results.items()}
        }
        
        try:
            cache.set(cache_key, response, 300)
        except:
            pass
        
        if user:
            try:
                AdvancedSearch._save_search_history(user, query)
            except:
                pass
        
        return response
    
    @staticmethod
    def _search_products(query):
        try:
            from goods.models import ListModel as Product
            
            products = Product.objects.filter(
                Q(goods_code__icontains=query) |
                Q(goods_desc__icontains=query) |
                Q(goods_brand__icontains=query),
                is_delete=False
            )[:20]
            
            results = []
            for p in products:
                relevance = 0
                # Use goods_desc as the product name
                product_name = p.goods_desc or p.goods_code
                
                if query.lower() in product_name.lower():
                    relevance += 10
                if query.lower() in p.goods_code.lower():
                    relevance += 5
                
                results.append({
                    'id': p.id,
                    'title': product_name,
                    'subtitle': f'Product - {p.goods_code} | ₹{p.goods_price or 0}',
                    'url': f'/products/{p.id}/',
                    'icon': 'box',
                    'relevance': relevance
                })
            
            return results
        except Exception as e:
            logger.error(f"Product search error: {e}")
            return []
    
    @staticmethod
    def _search_storage(query):
        try:
            from storage.models import StorageUnit
            
            units = StorageUnit.objects.filter(
                Q(unit_number__icontains=query) |
                Q(location__icontains=query) |
                Q(zone__icontains=query)
            )[:20]
            
            results = []
            for u in units:
                relevance = 12
                if query.lower() in u.unit_number.lower():
                    relevance += 8
                
                results.append({
                    'id': u.id,
                    'title': f'Storage Unit {u.unit_number}',
                    'subtitle': f'{u.get_type_display()} - {u.location} - ₹{u.price_per_month}/mo',
                    'url': f'/storage/{u.id}/',
                    'icon': 'warehouse',
                    'status': u.status,
                    'relevance': relevance
                })
            
            return results
        except Exception as e:
            logger.error(f"Storage search error: {e}")
            return []
    
    @staticmethod
    def _search_rentals(query):
        try:
            from rentals.models import RentalItem
            
            items = RentalItem.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            ).select_related('category')[:20]
            
            results = []
            for item in items:
                relevance = 11
                if query.lower() in item.name.lower():
                    relevance += 7
                
                category_name = item.category.name if item.category else 'Rental'
                price = item.daily_rate if item.daily_rate > 0 else item.hourly_rate
                price_label = '/day' if item.daily_rate > 0 else '/hour'
                
                results.append({
                    'id': item.id,
                    'title': item.name,
                    'subtitle': f'{category_name} - ₹{price}{price_label}',
                    'url': f'/rentals/{item.id}/',
                    'icon': 'tools',
                    'status': item.status,
                    'relevance': relevance
                })
            
            return results
        except Exception as e:
            logger.error(f"Rental search error: {e}")
            return []
    
    @staticmethod
    def _search_orders(query, user):
        try:
            from orders.models import Order
            
            orders = Order.objects.filter(
                Q(order_number__icontains=query)
            )[:20]
            
            results = []
            for o in orders:
                status_display = o.get_status_display() if hasattr(o, 'get_status_display') else o.status
                results.append({
                    'id': o.id,
                    'title': f'Order #{o.order_number}',
                    'subtitle': f'Status: {status_display}',
                    'url': f'/orders/{o.id}/',
                    'icon': 'shopping-cart',
                    'relevance': 8
                })
            
            return results
        except Exception as e:
            logger.error(f"Order search error: {e}")
            return []
    
    @staticmethod
    def _search_customers(query):
        try:
            from customer.models import ListModel as Customer
            
            customers = Customer.objects.filter(
                Q(customer_name__icontains=query) |
                Q(customer_contact__icontains=query),
                is_delete=False
            )[:20]
            
            results = []
            for c in customers:
                results.append({
                    'id': c.id,
                    'title': c.customer_name,
                    'subtitle': f'Customer - {c.customer_contact}',
                    'url': f'/customers/{c.id}/',
                    'icon': 'user',
                    'relevance': 7
                })
            
            return results
        except Exception as e:
            logger.error(f"Customer search error: {e}")
            return []
    
    @staticmethod
    def _search_suppliers(query):
        try:
            from supplier.models import ListModel as Supplier
            
            suppliers = Supplier.objects.filter(
                Q(supplier_name__icontains=query) |
                Q(supplier_contact__icontains=query),
                is_delete=False
            )[:20]
            
            results = []
            for s in suppliers:
                results.append({
                    'id': s.id,
                    'title': s.supplier_name,
                    'subtitle': f'Supplier - {s.supplier_contact}',
                    'url': f'/suppliers/{s.id}/',
                    'icon': 'truck',
                    'relevance': 6
                })
            
            return results
        except Exception as e:
            logger.error(f"Supplier search error: {e}")
            return []
    
    @staticmethod
    def _save_search_history(user, query):
        history_key = f'search_history_{user.id}'
        history = cache.get(history_key, [])
        
        if query not in history:
            history.insert(0, query)
            history = history[:10]
            cache.set(history_key, history, 86400*7)
    
    @staticmethod
    def get_search_history(user):
        return cache.get(f'search_history_{user.id}', [])
    
    @staticmethod
    def get_suggestions(query):
        if len(query) < 2:
            return []
        
        from goods.models import ListModel as Product
        
        suggestions = Product.objects.filter(
            goods_name__istartswith=query,
            is_delete=False
        ).values_list('goods_name', flat=True)[:5]
        
        return list(suggestions)
