from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.core.paginator import Paginator
from .models import AboutSection, TeamMember, Gallery, StaticContent
from permissions.decorators import get_user_role

def about_page(request):
    from django.contrib.auth import get_user_model
    from goods.models import ListModel
    from stock.models import StockListModel
    from customer.models import ListModel as Customer
    from supplier.models import ListModel as Supplier
    from warehouse.models import ListModel as Warehouse
    from orders.models import Order
    import json
    
    sections = AboutSection.objects.filter(is_active=True).order_by('order')
    team = TeamMember.objects.filter(is_active=True).order_by('order')
    gallery = Gallery.objects.filter(is_active=True).order_by('order')
    
    # Get or create static content
    mission, _ = StaticContent.objects.get_or_create(
        key='mission',
        defaults={'title': 'Our Mission', 'content': 'To provide businesses with a comprehensive, user-friendly platform for managing inventory, orders, warehouses, and logistics operations efficiently.'}
    )
    vision, _ = StaticContent.objects.get_or_create(
        key='vision',
        defaults={'title': 'Our Vision', 'content': 'To become the leading logistics management platform, empowering businesses of all sizes to streamline their supply chain operations.'}
    )
    
    user_role = get_user_role(request.user) if request.user.is_authenticated else 'guest'
    can_edit = user_role in ['superadmin', 'admin']
    
    User = get_user_model()
    context = {
        'sections': json.dumps(list(sections.values('id', 'title', 'content', 'order'))),
        'sections_list': sections,
        'team': team,
        'gallery': gallery,
        'mission': mission,
        'vision': vision,
        'can_edit': can_edit,
        'user_role': user_role,
        'total_users': User.objects.count(),
        'total_products': ListModel.objects.filter(is_delete=False).count(),
        'total_stock': StockListModel.objects.aggregate(total=models.Sum('goods_qty'))['total'] or 0,
        'total_orders': Order.objects.count(),
        'total_customers': Customer.objects.filter(is_delete=False).count(),
        'total_suppliers': Supplier.objects.filter(is_delete=False).count(),
        'total_warehouses': Warehouse.objects.filter(is_delete=False).count(),
        'recent_orders': Order.objects.order_by('-created_at')[:5]
    }
    
    # Use guest template for guest users, otherwise use default about template
    if user_role == 'guest':
        template = 'guest/about.html'
    else:
        template = 'about.html'
    
    return render(request, template, context)

@login_required
def manage_about(request):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        messages.error(request, 'Permission denied')
        return redirect('about:about_page')
    
    sections = AboutSection.objects.all().order_by('order')
    team = TeamMember.objects.all().order_by('order')
    gallery = Gallery.objects.all().order_by('order')
    
    # Pagination
    sections_page = Paginator(sections, 10).get_page(request.GET.get('s_page'))
    team_page = Paginator(team, 12).get_page(request.GET.get('t_page'))
    gallery_page = Paginator(gallery, 12).get_page(request.GET.get('g_page'))
    
    return render(request, 'about/manage.html', {
        'sections': sections_page,
        'team': team_page,
        'gallery': gallery_page
    })

@login_required
def create_section(request):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False}, status=403)
    
    if request.method == 'POST':
        section = AboutSection.objects.create(
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            order=request.POST.get('order', 0),
            created_by=request.user
        )
        if request.FILES.get('image'):
            section.image = request.FILES['image']
            section.save()
        messages.success(request, 'Section created')
        return redirect('about:manage_about')
    return JsonResponse({'success': False}, status=400)

@login_required
def update_section(request, pk):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False}, status=403)
    
    section = get_object_or_404(AboutSection, pk=pk)
    if request.method == 'POST':
        section.title = request.POST.get('title')
        section.content = request.POST.get('content')
        section.order = request.POST.get('order', 0)
        if request.FILES.get('image'):
            section.image = request.FILES['image']
        section.save()
        messages.success(request, 'Section updated')
        return redirect('about:about_page')
    return JsonResponse({'success': False}, status=400)

@login_required
def section_data(request, pk):
    section = get_object_or_404(AboutSection, pk=pk)
    return JsonResponse({
        'id': section.id,
        'title': section.title,
        'content': section.content,
        'order': section.order
    })

@login_required
def update_static(request, key):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False}, status=403)
    
    if request.method == 'POST':
        static = get_object_or_404(StaticContent, key=key)
        static.content = request.POST.get('content')
        static.save()
        messages.success(request, f'{static.title} updated')
        return redirect('about:about_page')
    return JsonResponse({'success': False}, status=400)

@login_required
def delete_section(request, pk):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False}, status=403)
    
    section = get_object_or_404(AboutSection, pk=pk)
    section.delete()
    messages.success(request, 'Section deleted')
    return redirect('about:manage_about')

@login_required
def create_team(request):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False}, status=403)
    
    if request.method == 'POST':
        member = TeamMember.objects.create(
            name=request.POST.get('name'),
            position=request.POST.get('position'),
            bio=request.POST.get('bio', ''),
            order=request.POST.get('order', 0)
        )
        if request.FILES.get('photo'):
            member.photo = request.FILES['photo']
            member.save()
        messages.success(request, 'Team member added')
        return redirect('about:manage_about')
    return JsonResponse({'success': False}, status=400)

@login_required
def delete_team(request, pk):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False}, status=403)
    
    member = get_object_or_404(TeamMember, pk=pk)
    member.delete()
    messages.success(request, 'Team member deleted')
    return redirect('about:manage_about')

@login_required
def create_gallery(request):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False}, status=403)
    
    if request.method == 'POST':
        gallery = Gallery.objects.create(
            title=request.POST.get('title'),
            order=request.POST.get('order', 0)
        )
        if request.FILES.get('image'):
            gallery.image = request.FILES['image']
            gallery.save()
        messages.success(request, 'Gallery image added')
        return redirect('about:manage_about')
    return JsonResponse({'success': False}, status=400)

@login_required
def delete_gallery(request, pk):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False}, status=403)
    
    gallery = get_object_or_404(Gallery, pk=pk)
    gallery.delete()
    messages.success(request, 'Gallery image deleted')
    return redirect('about:manage_about')
