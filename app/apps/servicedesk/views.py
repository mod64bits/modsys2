# servicedesk/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string, get_template
from django.contrib.auth.decorators import login_required
from .models import Ticket, WorkOrder, TicketComment, Attachment, Category
from apps.customers.models import Customer
from .forms import TicketForm, WorkOrderForm, TicketCommentForm
from django.contrib import messages
from django.db.models import Q, Case, When, Value, IntegerField
from django.db import models
from io import BytesIO
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

@login_required
def ticket_list(request):
    tickets = Ticket.objects.all()
    context = {
        'tickets': tickets,
        'page_title': 'Lista de Tickets'
    }
    return render(request, 'servicedesk/ticket_list.html', context)

@login_required
def ticket_create_modal(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            if request.user.is_authenticated:
                ticket.created_by = request.user
            ticket.save()
            return JsonResponse({'success': True, 'message': 'Ticket criado com sucesso!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = TicketForm()
    context = {
        'form': form,
        'form_title': 'Novo Ticket',
        'form_action_url': request.path
    }
    html_form = render_to_string('servicedesk/partials/ticket_form_modal_content.html', context, request=request)
    return HttpResponse(html_form)

@login_required
def ticket_delete_modal(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        ticket.delete()
        return JsonResponse({'success': True, 'message': 'Ticket excluído com sucesso!'})
    context = {'ticket': ticket, 'delete_title': f'Excluir Ticket #{pk}'}
    html_form = render_to_string('servicedesk/partials/ticket_delete_confirm_modal_content.html', context, request=request)
    return HttpResponse(html_form)

@login_required
def ticket_pdf_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    work_orders = ticket.work_orders.all().order_by('created_at')

    public_comments = ticket.comments.filter(
        is_internal_note=False,
        comment_type=TicketComment.CommentType.COMMENT
    ).select_related('author').prefetch_related('attachments').order_by('created_at')

    context = {
        'ticket': ticket,
        'work_orders': work_orders,
        'public_comments': public_comments,
        'company_name': 'Nome da Sua Empresa Aqui'
    }
    pdf = render_to_pdf('servicedesk/pdf/ticket_pdf_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Ticket_{ticket.id}.pdf"
        content = f"inline; filename='{filename}'"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Erro ao gerar PDF.", status=500)

@login_required
def work_order_list(request):
    work_orders = WorkOrder.objects.all()
    return render(request, 'servicedesk/work_order_list.html', {'work_orders': work_orders})

@login_required
def work_order_create_modal(request):
    # Lógica para criar OS
    pass

@login_required
def work_order_update_modal(request, pk):
    # Lógica para atualizar OS
    pass

@login_required
def work_order_detail_modal(request, pk):
    work_order = get_object_or_404(WorkOrder, pk=pk)
    context = {'work_order': work_order, 'detail_title': f'Detalhes da OS #{pk}'}
    html_content = render_to_string('servicedesk/partials/work_order_detail_modal_content.html', context, request=request)
    return HttpResponse(html_content)

@login_required
def work_order_delete_modal(request, pk):
    # Lógica para apagar OS
    pass

@login_required
def work_order_pdf_view(request, pk):
    # Lógica para gerar PDF da OS
    pass

@login_required
def add_ticket_comment(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        form = TicketCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()

            for f in request.FILES.getlist('attachments'):
                Attachment.objects.create(
                    comment=comment,
                    file=f,
                    uploaded_by=request.user
                )

            work_orders = ticket.work_orders.all()
            comments = ticket.comments.select_related('author').prefetch_related('attachments').all()
            comment_form = TicketCommentForm()
            context = {
                'ticket': ticket,
                'work_orders': work_orders,
                'comments': comments,
                'comment_form': comment_form,
                'detail_title': f'Detalhes do Ticket #{ticket.pk}'
            }
            html_content = render_to_string('servicedesk/partials/ticket_detail_modal_content.html', context, request=request)
            return JsonResponse({'success': True, 'html': html_content})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)

    return JsonResponse({'success': False, 'error': 'Pedido inválido.'}, status=400)

@login_required
def ticket_update_modal(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.status in ['FECHADO', 'RESOLVIDO']:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse(f'<div class="modal-header"><h5 class="modal-title">Ticket #{ticket.pk}</h5><button type="button" class="close" data-dismiss="modal">&times;</button></div><div class="modal-body"><p class="alert alert-warning">Este ticket está {ticket.get_status_display()} e não pode ser editado.</p></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-dismiss="modal">Fechar</button></div>')
        messages.warning(request, f'Ticket {ticket.get_status_display()} não pode ser editado.')
        return redirect('servicedesk:ticket_list')

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            original_status = ticket.get_status_display()
            original_assigned_to = ticket.assigned_to

            updated_ticket = form.save()

            log_entry = []
            if original_status != updated_ticket.get_status_display():
                log_entry.append(f'Status alterado de "{original_status}" para "{updated_ticket.get_status_display()}".')

            if original_assigned_to != updated_ticket.assigned_to:
                old_assignee = original_assigned_to.username if original_assigned_to else "ninguém"
                new_assignee = updated_ticket.assigned_to.username if updated_ticket.assigned_to else "ninguém"
                log_entry.append(f'Ticket atribuído a {new_assignee} (anteriormente {old_assignee}).')

            if log_entry:
                TicketComment.objects.create(
                    ticket=updated_ticket,
                    author=request.user,
                    comment="\n".join(log_entry),
                    comment_type=TicketComment.CommentType.LOG,
                    is_internal_note=True
                )

            work_orders = updated_ticket.work_orders.all()
            comments = updated_ticket.comments.select_related('author').prefetch_related('attachments').all()
            comment_form = TicketCommentForm()
            context = {
                'ticket': updated_ticket,
                'work_orders': work_orders,
                'comments': comments,
                'comment_form': comment_form,
                'detail_title': f'Detalhes do Ticket #{updated_ticket.pk}'
            }
            html_content = render_to_string('servicedesk/partials/ticket_detail_modal_content.html', context, request=request)
            return JsonResponse({'success': True, 'html': html_content, 'message': 'Ticket atualizado com sucesso!'})
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao atualizar o ticket.')
    else:
        form = TicketForm(instance=ticket)

    context = {
        'form': form,
        'ticket': ticket,
        'form_title': f'Editar Ticket #{ticket.pk}',
        'form_action_url': request.path
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('servicedesk/partials/ticket_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

@login_required
def ticket_detail_modal(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    work_orders = ticket.work_orders.all()
    comments = ticket.comments.select_related('author').prefetch_related('attachments').all()
    comment_form = TicketCommentForm()

    context = {
        'ticket': ticket,
        'work_orders': work_orders,
        'comments': comments,
        'comment_form': comment_form,
        'detail_title': f'Detalhes do Ticket #{ticket.pk}'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('servicedesk/partials/ticket_detail_modal_content.html', context, request=request)
        return HttpResponse(html_content)

    return JsonResponse({'error': 'Acesso direto não permitido ou esperado.'}, status=403)
