from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Category
from permissions.decorators import require_role

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def category_list(request):
    from goods.models import ListModel as Product
    from rentals.models import RentalItem
    from storage.models import StorageUnit
    from lockers.models import Locker
    from django.db.models import Count, Q
    
    categories = Category.objects.all()
    
    # Search
    search = request.GET.get('search', '')
    if search:
        categories = categories.filter(name__icontains=search) | categories.filter(code__icontains=search)
    
    # Filter by type
    cat_type = request.GET.get('type', '')
    if cat_type:
        categories = categories.filter(category_type=cat_type)
    
    # Add usage information
    for category in categories:
        # Check where category is used
        category.used_in_products = Product.objects.filter(goods_class=category.name, is_delete=False).exists()
        
        # Try to check rentals, storage, lockers - handle if models don't exist
        try:
            category.used_in_rentals = RentalItem.objects.filter(category=category).exists()
            rental_count = RentalItem.objects.filter(category=category).count()
        except:
            category.used_in_rentals = False
            rental_count = 0
            
        try:
            category.used_in_storage = StorageUnit.objects.filter(unit_type=category.name).exists()
            storage_count = StorageUnit.objects.filter(unit_type=category.name).count()
        except:
            category.used_in_storage = False
            storage_count = 0
            
        category.used_in_marketplace = Product.objects.filter(goods_class=category.name, is_delete=False).exists()
        
        try:
            category.used_in_lockers = Locker.objects.filter(locker_type=category.name).exists()
            locker_count = Locker.objects.filter(locker_type=category.name).count()
        except:
            category.used_in_lockers = False
            locker_count = 0
        
        # Count total usage
        category.usage_count = (
            Product.objects.filter(goods_class=category.name, is_delete=False).count() +
            rental_count + storage_count + locker_count
        )
    
    # Pagination
    paginator = Paginator(list(categories), 20)
    page = request.GET.get('page', 1)
    categories = paginator.get_page(page)
    
    context = {
        'categories': categories,
        'category_types': Category.CATEGORY_TYPES,
        'search': search,
        'selected_type': cat_type,
    }
    return render(request, 'categories/list.html', context)

@login_required
@require_role('superadmin', 'admin', 'supervisor')
def category_create(request):
    if request.method == 'POST':
        category = Category(
            name=request.POST['name'],
            code=request.POST['code'],
            category_type=request.POST['category_type'],
            icon=request.POST.get('icon', 'fa-folder'),
            description=request.POST.get('description', ''),
            status=request.POST.get('status', 'active'),
            created_by=request.user
        )
        category.save()
        messages.success(request, f'Category "{category.name}" created successfully!')
        return redirect('categories:list')
    
    return render(request, 'categories/form.html', {'category_types': Category.CATEGORY_TYPES})

@login_required
@require_role('superadmin', 'admin', 'supervisor')
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.name = request.POST['name']
        category.code = request.POST['code']
        category.category_type = request.POST['category_type']
        category.icon = request.POST.get('icon', 'fa-folder')
        category.description = request.POST.get('description', '')
        category.status = request.POST.get('status', 'active')
        category.save()
        messages.success(request, f'Category "{category.name}" updated successfully!')
        return redirect('categories:list')
    
    context = {'category': category, 'category_types': Category.CATEGORY_TYPES}
    return render(request, 'categories/form.html', context)

@login_required
@require_role('superadmin', 'admin')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully!')
        return redirect('categories:list')
    
    return render(request, 'categories/delete.html', {'category': category})

@login_required
def category_api(request):
    cat_type = request.GET.get('type', '')
    categories = Category.objects.filter(status='active')
    if cat_type:
        categories = categories.filter(category_type=cat_type)
    
    data = [{'id': c.id, 'name': c.name, 'code': c.code, 'icon': c.icon} for c in categories]
    return JsonResponse({'categories': data})
