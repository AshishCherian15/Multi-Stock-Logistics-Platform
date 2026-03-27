from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Ticket, TicketMessage

@login_required
def ticket_list(request):
    from permissions.decorators import get_user_role
    role = get_user_role(request.user)
    if role in ['superadmin','admin','supervisor','staff'] or request.user.is_staff:
        tickets = Ticket.objects.select_related('user','assigned_to').order_by('-created_at')
    else:
        tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tickets/list.html', {'tickets': tickets})

@login_required
def ticket_create(request):
    if request.method == 'POST':
        subject = request.POST.get('subject','').strip()
        description = request.POST.get('description','').strip()
        if subject and description:
            ticket = Ticket.objects.create(
                user=request.user, subject=subject, description=description,
                category=request.POST.get('category','other'),
                priority=request.POST.get('priority','medium'),
            )
            messages.success(request, f'Ticket {ticket.ticket_number} created.')
            return redirect('tickets:detail', ticket_id=ticket.id)
        messages.error(request, 'Subject and description required.')
    return render(request, 'tickets/create.html', {
        'categories': Ticket.CATEGORY_CHOICES, 'priorities': Ticket.PRIORITY_CHOICES
    })

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.user != request.user and not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('tickets:list')
    if request.method == 'POST':
        msg = request.POST.get('message','').strip()
        if msg:
            from permissions.decorators import get_user_role
            role = get_user_role(request.user)
            is_staff = role in ['superadmin','admin','supervisor','staff'] or request.user.is_staff
            TicketMessage.objects.create(ticket=ticket, user=request.user, message=msg, is_staff_reply=is_staff)
            messages.success(request, 'Reply added.')
            return redirect('tickets:detail', ticket_id=ticket.id)
    return render(request, 'tickets/detail.html', {
        'ticket': ticket,
        'ticket_messages': ticket.messages.select_related('user').order_by('created_at')
    })

@login_required
def ticket_update_status(request, ticket_id):
    if not request.user.is_staff:
        from permissions.decorators import get_user_role
        if get_user_role(request.user) not in ['superadmin','admin','supervisor','staff']:
            messages.error(request, 'Permission denied.')
            return redirect('tickets:list')
    ticket = get_object_or_404(Ticket, id=ticket_id)
    new_status = request.POST.get('status')
    if new_status in dict(Ticket.STATUS_CHOICES):
        ticket.status = new_status
        if new_status == 'resolved':
            ticket.resolved_at = timezone.now()
        ticket.save()
    return redirect('tickets:detail', ticket_id=ticket.id)
