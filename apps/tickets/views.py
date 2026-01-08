from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Ticket, TicketMessage

@login_required
def create_ticket(request):
    """Create a new support ticket"""
    if request.method == 'POST':
        ticket = Ticket.objects.create(
            user=request.user,
            subject=request.POST.get('subject'),
            description=request.POST.get('description'),
            category=request.POST.get('category', 'other'),
            priority=request.POST.get('priority', 'medium')
        )
        
        messages.success(request, f'Ticket {ticket.ticket_number} created successfully!')
        return redirect('tickets:detail', ticket_id=ticket.id)
    
    return render(request, 'tickets/create.html')

@login_required
def ticket_list(request):
    """List all user's tickets"""
    status_filter = request.GET.get('status', 'all')
    
    tickets = Ticket.objects.filter(user=request.user)
    
    if status_filter != 'all':
        tickets = tickets.filter(status=status_filter)
    
    context = {
        'tickets': tickets,
        'status_filter': status_filter,
        'open_count': Ticket.objects.filter(user=request.user, status='open').count(),
        'in_progress_count': Ticket.objects.filter(user=request.user, status='in_progress').count(),
        'resolved_count': Ticket.objects.filter(user=request.user, status='resolved').count(),
    }
    return render(request, 'tickets/list.html', context)

@login_required
def ticket_detail(request, ticket_id):
    """View ticket details and conversation"""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            TicketMessage.objects.create(
                ticket=ticket,
                user=request.user,
                message=message_text,
                is_staff_reply=False
            )
            
            # Update ticket status if it was closed
            if ticket.status == 'closed':
                ticket.status = 'open'
                ticket.save()
            
            messages.success(request, 'Message added successfully!')
            return redirect('tickets:detail', ticket_id=ticket.id)
    
    ticket_messages = ticket.messages.all().select_related('user')
    
    context = {
        'ticket': ticket,
        'messages': ticket_messages,
    }
    return render(request, 'tickets/detail.html', context)

@login_required
def close_ticket(request, ticket_id):
    """Close a ticket"""
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
        ticket.status = 'closed'
        ticket.save()
        
        messages.success(request, 'Ticket closed successfully!')
        return redirect('tickets:detail', ticket_id=ticket.id)
    
    return redirect('tickets:list')
