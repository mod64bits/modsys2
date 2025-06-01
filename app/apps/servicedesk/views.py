# servicedesk/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required # Importante para proteger views
from .models import Ticket, WorkOrder, User # Adicionado User para assigned_technician
from .forms import TicketForm, WorkOrderForm
from django.contrib import messages # Para feedback ao usuário

# @login_required # Descomente para exigir login
def ticket_list(request):
    tickets = Ticket.objects.all() # Ou filtre conforme necessário, ex: request.user
    context = {
        'tickets': tickets,
        'page_title': 'Lista de Tickets'
    }
    return render(request, 'servicedesk/ticket_list.html', context)

# @login_required
def ticket_create_modal(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            if request.user.is_authenticated: # Garante que o usuário está logado
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
        form = TicketForm(user=request.user)

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
    work_orders = ticket.work_orders.all() # Carrega OS relacionadas
    # comments = ticket.comments.all() # Se tiver comentários

    context = {
        'ticket': ticket,
        'work_orders': work_orders, # Adiciona OS ao contexto
        # 'comments': comments,
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
    # Buscar todos os tickets para popular o select no template
    # Idealmente, filtre por tickets que podem receber novas OS (ex: não fechados)
    tickets_for_wo = Ticket.objects.exclude(status__in=['FECHADO', 'RESOLVIDO']) # Exemplo de filtro
    # Ou simplesmente todos:
    # tickets_for_wo = Ticket.objects.all()

    context = {
        'work_orders': work_orders,
        'tickets_for_wo_creation': tickets_for_wo, # Adicionado ao contexto
        'page_title': 'Lista de Ordens de Serviço'
    }
    return render(request, 'servicedesk/work_order_list.html', context)

# @login_required
def work_order_create_modal(request):
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
        form = WorkOrderForm()
        ticket_id = request.GET.get('ticket_id')
        if ticket_id:
            try:
                # Garante que o ticket exista e não esteja em um estado que impeça novas OS
                ticket = Ticket.objects.exclude(status__in=['FECHADO', 'RESOLVIDO']).get(pk=ticket_id)
                form.fields['ticket'].initial = ticket
                # Você pode querer tornar o campo 'ticket' readonly se ele for pré-selecionado
                # form.fields['ticket'].widget.attrs['disabled'] = True
                # Cuidado: campos desabilitados não são enviados no POST,
                # então você precisaria pegar o ticket_id de outra forma no POST ou não desabilitar.
            except Ticket.DoesNotExist:
                messages.warning(request, f"Ticket com ID {ticket_id} não encontrado ou não apto para novas OS.")


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
