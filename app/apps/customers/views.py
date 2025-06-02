# customers/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .models import Customer
from apps.servicedesk.models import Ticket, WorkOrder # Para buscar tickets/OS do cliente
from .forms import CustomerForm
from django.contrib import messages
from django.db.models import Q, Case, When, Value, IntegerField # Importar Case, When, Value, IntegerField
from django.db import models # Adicionada a importação que faltava

# @login_required
def customer_list(request):
    customers = Customer.objects.all()
    context = {
        'customers': customers,
        'page_title': 'Lista de Clientes'
    }
    return render(request, 'customers/customer_list.html', context)

# @login_required
def customer_create_modal(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Cliente criado com sucesso!', 'customer_id': customer.pk, 'customer_name': str(customer)})
            messages.success(request, 'Cliente criado com sucesso!')
            return redirect('customers:customer_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao criar o cliente. Verifique os dados.')
    else:
        form = CustomerForm()

    context = {
        'form': form,
        'form_title': 'Novo Cliente',
        'form_action_url': request.path
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('customers/partials/customer_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

# @login_required
def customer_update_modal(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Cliente atualizado com sucesso!'})
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('customers:customer_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao atualizar o cliente.')
    else:
        form = CustomerForm(instance=customer)

    context = {
        'form': form,
        'customer': customer,
        'form_title': f'Editar Cliente: {customer.nome}',
        'form_action_url': request.path
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('customers/partials/customer_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

# @login_required
def customer_detail_modal(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    # Buscar tickets e ordens de serviço relacionados, ordenando os abertos primeiro
    tickets = customer.tickets.all().order_by(
        Case( # Agora Case é importado diretamente de django.db.models
            When(status__in=['ABERTO', 'EM_ANDAMENTO', 'AGUARDANDO_CLIENTE'], then=Value(0)),
            When(status='RESOLVIDO', then=Value(1)),
            When(status='FECHADO', then=Value(2)),
            default=Value(3),
            output_field=IntegerField(), # IntegerField também precisa ser importado
        ),
        '-created_at' # Mais recentes primeiro dentro de cada grupo de status
    )

    # Para ordens de serviço, podemos pegar todas as OS dos tickets do cliente
    work_orders_query = WorkOrder.objects.filter(ticket__customer=customer)
    work_orders = work_orders_query.order_by(
        Case(
            When(status__in=['PENDENTE', 'AGENDADA', 'EM_EXECUCAO'], then=Value(0)),
            When(status='CONCLUIDA', then=Value(1)),
            When(status='CANCELADA', then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        ),
        '-created_at'
    )

    context = {
        'customer': customer,
        'tickets': tickets,
        'work_orders': work_orders,
        'detail_title': f'Detalhes do Cliente: {customer.nome}'
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('customers/partials/customer_detail_modal_content.html', context, request=request)
        return HttpResponse(html_content)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

# @login_required
def customer_delete_modal(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer_name = customer.nome
        customer.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Cliente {customer_name} excluído com sucesso!'})
        messages.success(request, f'Cliente {customer_name} excluído com sucesso!')
        return redirect('customers:customer_list')

    context = {
        'customer': customer,
        'delete_title': f'Confirmar Exclusão do Cliente: {customer.nome}',
        'form_action_url': request.path
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('customers/partials/customer_delete_confirm_modal_content.html', context, request=request)
        return HttpResponse(html_content)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)
