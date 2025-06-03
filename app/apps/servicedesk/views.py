# servicedesk/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string, get_template
from django.contrib.auth.decorators import login_required
from .models import Ticket, WorkOrder, User
from apps.customers.models import Customer
from .forms import TicketForm, WorkOrderForm
from django.contrib import messages
from django.db.models import Q, Case, When, Value, IntegerField
from django.db import models

# Para PDF
from io import BytesIO
from xhtml2pdf import pisa # Importar pisa

# Função auxiliar para renderizar PDF
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result) # Alterado para UTF-8
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

# @login_required
def ticket_list(request):
    tickets = Ticket.objects.all()
    context = {
        'tickets': tickets,
        'page_title': 'Lista de Tickets'
    }
    return render(request, 'servicedesk/ticket_list.html', context)

# @login_required
def ticket_create_modal(request):
    initial_data = {}
    customer_id = request.GET.get('customer_id')
    if customer_id:
        try:
            customer = Customer.objects.get(pk=customer_id)
            initial_data['customer'] = customer
        except Customer.DoesNotExist:
            messages.warning(request, f"Cliente com ID {customer_id} não encontrado.")

    if request.method == 'POST':
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            if request.user.is_authenticated:
                ticket.created_by = request.user
            ticket.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Ticket criado com sucesso!'})
            messages.success(request, 'Ticket criado com sucesso!')
            return redirect('servicedesk:ticket_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao criar o ticket. Verifique os dados.')
    else:
        form = TicketForm(user=request.user, initial=initial_data)

    context = {
        'form': form,
        'form_title': 'Abrir Novo Ticket',
        'form_action_url': request.path
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('servicedesk/partials/ticket_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)

    return JsonResponse({'error': 'Acesso direto não permitido ou esperado.'}, status=403)


# @login_required
def ticket_update_modal(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.status in ['FECHADO', 'RESOLVIDO']:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse(f'<div class="modal-header"><h5 class="modal-title">Ticket #{ticket.pk}</h5><button type="button" class="close" data-dismiss="modal">&times;</button></div><div class="modal-body"><p class="alert alert-warning">Este ticket está {ticket.get_status_display()} e não pode ser editado.</p></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-dismiss="modal">Fechar</button></div>')
        messages.warning(request, f'Ticket {ticket.get_status_display()} não pode ser editado.')
        return redirect('servicedesk:ticket_list')


    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket, user=request.user)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Ticket atualizado com sucesso!'})
            messages.success(request, 'Ticket atualizado com sucesso!')
            return redirect('servicedesk:ticket_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao atualizar o ticket.')
    else:
        form = TicketForm(instance=ticket, user=request.user)

    context = {
        'form': form,
        'ticket': ticket,
        'form_title': f'Editar Ticket #{ticket.pk}',
        'form_action_url': request.path
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('servicedesk/partials/ticket_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)

    return JsonResponse({'error': 'Acesso direto não permitido ou esperado.'}, status=403)


# @login_required
def ticket_detail_modal(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    work_orders = ticket.work_orders.all()
    context = {
        'ticket': ticket,
        'work_orders': work_orders,
        'detail_title': f'Detalhes do Ticket #{ticket.pk}'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('servicedesk/partials/ticket_detail_modal_content.html', context, request=request)
        return HttpResponse(html_content)

    return JsonResponse({'error': 'Acesso direto não permitido ou esperado.'}, status=403)


# @login_required
def ticket_delete_modal(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        ticket_id = ticket.id
        ticket.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Ticket #{ticket_id} excluído com sucesso!'})
        messages.success(request, f'Ticket #{ticket_id} excluído com sucesso!')
        return redirect('servicedesk:ticket_list')

    context = {
        'ticket': ticket,
        'delete_title': f'Confirmar Exclusão do Ticket #{ticket.pk}',
        'form_action_url': request.path
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('servicedesk/partials/ticket_delete_confirm_modal_content.html', context, request=request)
        return HttpResponse(html_content)

    return JsonResponse({'error': 'Acesso direto não permitido ou esperado.'}, status=403)


# Views para WorkOrder
# @login_required
def work_order_list(request):
    work_orders = WorkOrder.objects.all()
    tickets_for_wo = Ticket.objects.exclude(status__in=['FECHADO', 'RESOLVIDO'])

    context = {
        'work_orders': work_orders,
        'tickets_for_wo_creation': tickets_for_wo,
        'page_title': 'Lista de Ordens de Serviço'
    }
    return render(request, 'servicedesk/work_order_list.html', context)

# @login_required
def work_order_create_modal(request):
    initial_data = {}
    ticket_id = request.GET.get('ticket_id')
    customer_id = request.GET.get('customer_id')

    if ticket_id:
        try:
            ticket = Ticket.objects.exclude(status__in=['FECHADO', 'RESOLVIDO']).get(pk=ticket_id)
            initial_data['ticket'] = ticket
        except Ticket.DoesNotExist:
            messages.warning(request, f"Ticket com ID {ticket_id} não encontrado ou não apto para novas OS.")
    elif customer_id:
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
             messages.warning(request, f"Cliente com ID {customer_id} não encontrado.")


    if request.method == 'POST':
        form = WorkOrderForm(request.POST)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Ordem de Serviço criada com sucesso!'})
            messages.success(request, 'Ordem de Serviço criada com sucesso!')
            return redirect('servicedesk:work_order_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao criar a Ordem de Serviço. Verifique os dados.')
    else:
        form = WorkOrderForm(initial=initial_data)
        if customer_id and not ticket_id:
             form.fields['ticket'].queryset = Ticket.objects.filter(customer_id=customer_id).exclude(status__in=['FECHADO', 'RESOLVIDO'])


    context = {
        'form': form,
        'form_title': 'Nova Ordem de Serviço',
        'form_action_url': request.path
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('servicedesk/partials/work_order_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)

    return JsonResponse({'error': 'Acesso direto não permitido ou esperado.'}, status=403)

# @login_required
def work_order_update_modal(request, pk):
    work_order = get_object_or_404(WorkOrder, pk=pk)
    if work_order.status in ['CONCLUIDA', 'CANCELADA']:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse(f'<div class="modal-header"><h5 class="modal-title">OS #{work_order.pk}</h5><button type="button" class="close" data-dismiss="modal">&times;</button></div><div class="modal-body"><p class="alert alert-warning">Esta OS está {work_order.get_status_display()} e não pode ser editada.</p></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-dismiss="modal">Fechar</button></div>')
        messages.warning(request, f'OS {work_order.get_status_display()} não pode ser editada.')
        return redirect('servicedesk:work_order_list')

    if request.method == 'POST':
        form = WorkOrderForm(request.POST, instance=work_order)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Ordem de Serviço atualizada com sucesso!'})
            messages.success(request, 'Ordem de Serviço atualizada com sucesso!')
            return redirect('servicedesk:work_order_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao atualizar a Ordem de Serviço.')
    else:
        form = WorkOrderForm(instance=work_order)

    context = {
        'form': form,
        'work_order': work_order,
        'form_title': f'Editar Ordem de Serviço #{work_order.pk}',
        'form_action_url': request.path
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('servicedesk/partials/work_order_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)

    return JsonResponse({'error': 'Acesso direto não permitido ou esperado.'}, status=403)

# @login_required
def work_order_detail_modal(request, pk):
    work_order = get_object_or_404(WorkOrder, pk=pk)
    context = {
        'work_order': work_order,
        'detail_title': f'Detalhes da Ordem de Serviço #{work_order.pk}'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('servicedesk/partials/work_order_detail_modal_content.html', context, request=request)
        return HttpResponse(html_content)

    return JsonResponse({'error': 'Acesso direto não permitido ou esperado.'}, status=403)

# @login_required
def work_order_delete_modal(request, pk):
    work_order = get_object_or_404(WorkOrder, pk=pk)
    if request.method == 'POST':
        work_order_id = work_order.id
        work_order.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Ordem de Serviço #{work_order_id} excluída com sucesso!'})
        messages.success(request, f'Ordem de Serviço #{work_order_id} excluída com sucesso!')
        return redirect('servicedesk:work_order_list')

    context = {
        'work_order': work_order,
        'delete_title': f'Confirmar Exclusão da Ordem de Serviço #{work_order.pk}',
        'form_action_url': request.path
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('servicedesk/partials/work_order_delete_confirm_modal_content.html', context, request=request)
        return HttpResponse(html_content)

    return JsonResponse({'error': 'Acesso direto não permitido ou esperado.'}, status=403)


# Novas Views para PDF
# @login_required
def ticket_pdf_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    work_orders = ticket.work_orders.all().order_by('created_at')
    context = {
        'ticket': ticket,
        'work_orders': work_orders,
        'company_name': 'Nome da Sua Empresa Aqui' # Você pode pegar isso das configurações ou de um modelo
    }
    pdf = render_to_pdf('servicedesk/pdf/ticket_pdf_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Ticket_{ticket.id}.pdf"
        content = f"inline; filename='{filename}'" # Mostra no navegador
        # content = f"attachment; filename='{filename}'" # Força download
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Erro ao gerar PDF.", status=500)

# @login_required
def work_order_pdf_view(request, pk):
    work_order = get_object_or_404(WorkOrder, pk=pk)
    context = {
        'work_order': work_order,
        'company_name': 'Nome da Sua Empresa Aqui'
    }
    pdf = render_to_pdf('servicedesk/pdf/work_order_pdf_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"OS_{work_order.id}.pdf"
        content = f"inline; filename='{filename}'"
        # content = f"attachment; filename='{filename}'"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Erro ao gerar PDF.", status=500)
