# servicedesk/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string, get_template
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Ticket, WorkOrder, TicketComment, Attachment, Category, ProdutoUtilizadoOS
from apps.customers.models import Customer
from .forms import TicketForm, WorkOrderForm, TicketCommentForm, ProdutoUtilizadoOSFormSet
from apps.inventory.models import Produto
from io import BytesIO
from xhtml2pdf import pisa

# -- Função Auxiliar para PDF --
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

# --- Views de Ticket ---

@login_required
def ticket_list(request):
    tickets = Ticket.objects.select_related('customer', 'assigned_to').all()
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
                    ticket=updated_ticket, author=request.user, comment="\n".join(log_entry),
                    comment_type=TicketComment.CommentType.LOG, is_internal_note=True
                )
            # Retorna o conteúdo atualizado do modal de detalhes
            return redirect('servicedesk:ticket_detail_modal', pk=updated_ticket.pk)
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = TicketForm(instance=ticket)

    context = {'form': form, 'ticket': ticket, 'form_title': f'Editar Ticket #{ticket.pk}', 'form_action_url': request.path}
    html_form = render_to_string('servicedesk/partials/ticket_form_modal_content.html', context, request=request)
    return HttpResponse(html_form)

@login_required
def ticket_detail_modal(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    work_orders = ticket.work_orders.all()
    comments = ticket.comments.select_related('author').prefetch_related('attachments').all()
    comment_form = TicketCommentForm()
    context = {
        'ticket': ticket, 'work_orders': work_orders, 'comments': comments,
        'comment_form': comment_form, 'detail_title': f'Detalhes do Ticket #{ticket.pk}'
    }
    html_content = render_to_string('servicedesk/partials/ticket_detail_modal_content.html', context, request=request)
    return HttpResponse(html_content)

@login_required
def ticket_delete_modal(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        ticket.delete()
        return JsonResponse({'success': True, 'message': 'Ticket excluído com sucesso!'})
    context = {'ticket': ticket, 'delete_title': f'Excluir Ticket #{pk}', 'form_action_url': request.path}
    html_form = render_to_string('servicedesk/partials/ticket_delete_confirm_modal_content.html', context, request=request)
    return HttpResponse(html_form)

@login_required
def ticket_pdf_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    work_orders = ticket.work_orders.all().order_by('created_at')
    public_comments = ticket.comments.filter(is_internal_note=False, comment_type=TicketComment.CommentType.COMMENT).select_related('author').prefetch_related('attachments').order_by('created_at')
    context = {'ticket': ticket, 'work_orders': work_orders, 'public_comments': public_comments, 'company_name': 'Sua Empresa'}
    pdf = render_to_pdf('servicedesk/pdf/ticket_pdf_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Ticket_{ticket.id}.pdf"
        content = f"inline; filename=\"{filename}\""
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Erro ao gerar PDF.", status=500)

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
                Attachment.objects.create(comment=comment, file=f, uploaded_by=request.user)
            return redirect('servicedesk:ticket_detail_modal', pk=ticket.pk)
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    return JsonResponse({'success': False, 'error': 'Pedido inválido.'}, status=400)


# --- Views de Ordem de Serviço ---

@login_required
def work_order_list(request):
    work_orders = WorkOrder.objects.select_related('ticket__customer', 'assigned_technician').all()
    return render(request, 'servicedesk/work_order_list.html', {'work_orders': work_orders, 'page_title': 'Ordens de Serviço'})

@login_required
def work_order_create_view(request):
    if request.method == 'POST':
        form = WorkOrderForm(request.POST)
        if form.is_valid():
            work_order = form.save()
            messages.success(request, f"Ordem de Serviço #{work_order.id} criada. Adicione produtos se necessário.")
            return redirect('servicedesk:work_order_update', pk=work_order.pk)
    else:
        form = WorkOrderForm()

    context = {
        'form': form,
        'product_formset': ProdutoUtilizadoOSFormSet(prefix='produtos'),
        'page_title': "Criar Nova Ordem de Serviço"
    }
    return render(request, 'servicedesk/work_order_form.html', context)

@login_required
def work_order_update_view(request, pk):
    work_order = get_object_or_404(WorkOrder, pk=pk)
    if work_order.status in ['CONCLUIDA', 'CANCELADA']:
        messages.error(request, "Ordens de Serviço concluídas ou canceladas não podem ser editadas.")
        return redirect('servicedesk:work_order_list')
    if request.method == 'POST':
        form = WorkOrderForm(request.POST, instance=work_order)
        product_formset = ProdutoUtilizadoOSFormSet(request.POST, instance=work_order, prefix='produtos')
        if form.is_valid() and product_formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    instances = product_formset.save(commit=False)
                    for instance in instances:
                        if not instance.pk and instance.produto:
                            instance.preco_compra_no_momento = instance.produto.preco_compra
                            instance.preco_venda_no_momento = instance.produto.preco_venda_sugerido or instance.produto.preco_compra
                        instance.save()
                    product_formset.save_m2m()
                    for form_deleted in product_formset.deleted_forms:
                        if form_deleted.instance.pk:
                            form_deleted.instance.delete()
                messages.success(request, "Ordem de Serviço atualizada com sucesso.")
                return redirect('servicedesk:work_order_list')
            except Exception as e:
                messages.error(request, f"Ocorreu um erro: {e}")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = WorkOrderForm(instance=work_order)
        product_formset = ProdutoUtilizadoOSFormSet(instance=work_order, prefix='produtos')
    context = {
        'form': form, 'product_formset': product_formset, 'work_order': work_order,
        'page_title': f"Editar Ordem de Serviço #{work_order.id}"
    }
    return render(request, 'servicedesk/work_order_form.html', context)

@login_required
def work_order_detail_modal(request, pk):
    work_order = get_object_or_404(WorkOrder, pk=pk)
    produtos_utilizados = work_order.produtos_utilizados.select_related('produto').all()
    context = {
        'work_order': work_order, 'produtos_utilizados': produtos_utilizados,
        'detail_title': f'Detalhes da OS #{pk}'
    }
    html_content = render_to_string('servicedesk/partials/work_order_detail_modal_content.html', context, request=request)
    return HttpResponse(html_content)

@login_required
def work_order_delete_modal(request, pk):
    work_order = get_object_or_404(WorkOrder, pk=pk)
    if request.method == 'POST':
        work_order.delete()
        return JsonResponse({'success': True, 'message': 'Ordem de Serviço excluída com sucesso!'})
    context = {'work_order': work_order, 'delete_title': f'Excluir OS #{pk}', 'form_action_url': request.path}
    html_form = render_to_string('servicedesk/partials/work_order_delete_confirm_modal_content.html', context, request=request)
    return HttpResponse(html_form)

@login_required
def work_order_pdf_view(request, pk):
    work_order = get_object_or_404(WorkOrder.objects.select_related('ticket__customer'), pk=pk)
    context = {'work_order': work_order, 'company_name': 'Sua Empresa'}
    pdf = render_to_pdf('servicedesk/pdf/work_order_pdf_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="OS_{pk}.pdf"'
        return response
    return HttpResponse("Erro ao gerar PDF da OS.", status=500)
