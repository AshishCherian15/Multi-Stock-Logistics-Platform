from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .advanced_search import AdvancedSearch

@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    
    # Always return JSON for AJAX requests
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax')
    
    if not query:
        if is_ajax:
            return JsonResponse({'results': [], 'count': 0, 'by_category': {}})
        return render(request, 'search/results.html', {'query': '', 'results': [], 'count': 0, 'by_category': {}})
    
    try:
        results = AdvancedSearch.search_all(query, request.user)
    except Exception as e:
        # Fallback search if advanced search fails
        try:
            from goods.models import ListModel as Product
            from customer.models import ListModel as Customer
            
            products = Product.objects.filter(
                Q(goods_code__icontains=query) | Q(goods_desc__icontains=query),
                is_delete=False
            )[:5]
            customers = Customer.objects.filter(customer_name__icontains=query, is_delete=False)[:5]
            
            results = {
                'results': [
                    *[{'title': p.goods_desc or p.goods_code, 'subtitle': f'Product - {p.goods_code}', 'url': f'/products/{p.id}/', 'icon': 'box', 'category': 'products'} for p in products],
                    *[{'title': c.customer_name, 'subtitle': f'Customer - {c.customer_city}', 'url': f'/customers/', 'icon': 'user', 'category': 'customers'} for c in customers],
                ],
                'count': len(products) + len(customers),
                'by_category': {'products': len(products), 'customers': len(customers)}
            }
        except Exception as fallback_error:
            if is_ajax:
                return JsonResponse({
                    'results': [],
                    'count': 0,
                    'by_category': {},
                    'error': 'Search temporarily unavailable'
                })
            return render(request, 'search/results.html', {
                'query': query,
                'results': [],
                'count': 0,
                'by_category': {},
                'error': 'Search temporarily unavailable'
            })
    
    # Always return JSON for AJAX requests
    if is_ajax:
        return JsonResponse(results)
    
    # Render HTML page for direct access
    return render(request, 'search/results.html', {
        'query': query,
        'results': results.get('results', []),
        'count': results.get('count', 0),
        'by_category': results.get('by_category', {})
    })

@login_required
def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    
    try:
        suggestions = AdvancedSearch.get_suggestions(query)
        return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        return JsonResponse({'suggestions': [], 'error': str(e)}, status=500)

@login_required
def search_history(request):
    try:
        history = AdvancedSearch.get_search_history(request.user)
        return JsonResponse({'history': history})
    except Exception as e:
        return JsonResponse({'history': [], 'error': str(e)}, status=500)
