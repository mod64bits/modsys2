# dashboard/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Q, F
from django.db import models
from django.db.models.functions import TruncMonth, ExtractYear
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from calendar import month_name

from apps.servicedesk.models import Ticket, WorkOrder
from apps.quotes.models import Orcamento
from apps.financial.models import ContaReceber, Pagamento
from .forms import QuickTicketStatusUpdateForm, QuickWorkOrderStatusUpdateForm, QuickOrcamentoStatusUpdateForm

@login_required
def dashboard_view(request):
    """
    Renderiza a página principal do dashboard geral.
    """
    end_date = timezone.now()
    start_date_activities = end_date - timedelta(days=30)
    start_date_billing = end_date.replace(month=1, day=1)

    available_years = Orcamento.objects.annotate(year=ExtractYear('created_at')).values_list('year', flat=True).distinct().order_by('-year')
    current_year = end_date.year
    previous_year = current_year - 1

    recent_open_tickets = Ticket.objects.filter(status__in=['ABERTO', 'EM_ANDAMENTO']).select_related('customer').order_by('-created_at')[:10]
    recent_open_work_orders = WorkOrder.objects.filter(status__in=['PENDENTE', 'EM_EXECUCAO', 'AGENDADA']).select_related('ticket__customer').order_by('-created_at')[:10]
    recent_pending_quotes = Orcamento.objects.exclude(status__in=['APROVADO', 'REPROVADO', 'CONCLUIDO', 'CANCELADO']).select_related('cliente').order_by('-created_at')[:10]

    context = {
        'page_title': 'Dashboard',
        'activity_start_date': start_date_activities.strftime('%Y-%m-%d'),
        'activity_end_date': end_date.strftime('%Y-%m-%d'),
        'available_years': list(available_years),
        'current_year': current_year,
        'previous_year': previous_year,
        'recent_open_tickets': recent_open_tickets,
        'recent_open_work_orders': recent_open_work_orders,
        'recent_pending_quotes': recent_pending_quotes,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def financial_dashboard_view(request):
    """
    Renderiza a página principal do dashboard financeiro com KPIs corrigidos.
    """
    today = timezone.now().date()

    # CORREÇÃO: Cálculos de KPI ajustados para usar agregações de base de dados corretas
    total_recebido = Pagamento.objects.all().aggregate(total=Sum('valor_pago'))['total'] or 0
    total_a_receber = ContaReceber.objects.exclude(status__in=['PAGO', 'CANCELADO']).aggregate(saldo=Sum(F('valor_total') - F('valor_pago')))['saldo'] or 0
    total_vencido = ContaReceber.objects.filter(status='VENCIDO').aggregate(saldo=Sum(F('valor_total') - F('valor_pago')))['saldo'] or 0

    contas = ContaReceber.objects.select_related('cliente').order_by('data_vencimento')

    context = {
        'page_title': 'Dashboard Financeiro',
        'total_recebido': total_recebido,
        'total_a_receber': total_a_receber,
        'total_vencido': total_vencido,
        'contas_a_receber': contas,
    }
    return render(request, 'dashboard/financial_dashboard.html', context)


@login_required
def dashboard_data_api(request):
    """
    API AJAX unificada que retorna dados para todos os gráficos do dashboard.
    """
    data_type = request.GET.get('data_type', 'all')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    data = {}

    # Lógica para Atividades
    if data_type == 'activities':
        start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date_for_query = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date() + timedelta(days=1)

        tickets_por_status = Ticket.objects.filter(created_at__gte=start_date, created_at__lt=end_date_for_query).values('status').annotate(count=Count('id')).order_by('status')
        os_por_status = WorkOrder.objects.filter(created_at__gte=start_date, created_at__lt=end_date_for_query).values('status').annotate(count=Count('id')).order_by('status')
        data['tickets_por_status'] = list(tickets_por_status)
        data['os_por_status'] = list(os_por_status)

    # Lógica para Faturamento
    elif data_type == 'billing':
        year1 = int(request.GET.get('year1') or timezone.now().year)
        year2 = int(request.GET.get('year2') or 0)

        faturamento_total_periodo = Orcamento.objects.filter(status='APROVADO', created_at__year=year1).aggregate(total=Sum('valor_total_orcamento'))['total'] or 0
        vendas_ano_1 = Orcamento.objects.filter(status='APROVADO', created_at__year=year1).annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('valor_total_orcamento')).order_by('month')

        labels_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        dados_ano_1 = [0] * 12
        dados_ano_2 = [0] * 12

        for venda in vendas_ano_1:
            dados_ano_1[venda['month'].month - 1] = float(venda['total'] or 0)

        if year2 > 0:
            vendas_ano_2_query = Orcamento.objects.filter(status='APROVADO', created_at__year=year2).annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('valor_total_orcamento')).order_by('month')
            for venda in vendas_ano_2_query:
                dados_ano_2[venda['month'].month - 1] = float(venda['total'] or 0)

        data['faturamento_ao_longo_do_tempo'] = {
            'total_geral': float(faturamento_total_periodo),
            'labels': labels_meses,
            'ano1': {'label': str(year1), 'data': dados_ano_1},
            'ano2': {'label': str(year2), 'data': dados_ano_2}
        }

    # Lógica para o Gráfico Financeiro
    elif data_type == 'financial_chart':
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=180)
        faturamento_mensal = ContaReceber.objects.filter(data_emissao__gte=six_months_ago).annotate(month=TruncMonth('data_emissao')).values('month').annotate(total=Sum('valor_total')).order_by('month')
        recebimentos_mensais = Pagamento.objects.filter(data_pagamento__gte=six_months_ago).annotate(month=TruncMonth('data_pagamento')).values('month').annotate(total=Sum('valor_pago')).order_by('month')

        labels, faturamento_data, recebimentos_data = [], [], []
        faturamento_dict = {item['month'].strftime('%Y-%m'): float(item['total'] or 0) for item in faturamento_mensal}
        recebimentos_dict = {item['month'].strftime('%Y-%m'): float(item['total'] or 0) for item in recebimentos_mensais}

        current_month = six_months_ago.replace(day=1)
        while current_month <= today.replace(day=1):
            month_key = current_month.strftime('%Y-%m'); month_label = current_month.strftime('%b/%y')
            labels.append(month_label)
            faturamento_data.append(faturamento_dict.get(month_key, 0))
            recebimentos_data.append(recebimentos_dict.get(month_key, 0))
            next_month = current_month.month % 12 + 1; next_year = current_month.year + current_month.month // 12
            current_month = current_month.replace(year=next_year, month=next_month)

        data['labels'] = labels
        data['faturamento'] = faturamento_data
        data['recebimentos'] = recebimentos_data

    return JsonResponse(data)




@login_required
def update_status_modal(request, model_name, pk):
    """
    View para o modal de atualização rápida de status de Ticket, OS ou Orçamento.
    """
    if model_name == 'ticket':
        ModelClass = Ticket
        FormClass = QuickTicketStatusUpdateForm
    elif model_name == 'workorder':
        ModelClass = WorkOrder
        FormClass = QuickWorkOrderStatusUpdateForm
    elif model_name == 'orcamento':
        ModelClass = Orcamento
        FormClass = QuickOrcamentoStatusUpdateForm
    else:
        return HttpResponse("Tipo de modelo inválido.", status=400)

    instance = get_object_or_404(ModelClass, pk=pk)

    if request.method == 'POST':
        form = FormClass(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Status atualizado com sucesso!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = FormClass(instance=instance)

    context = {
        'form': form,
        'instance': instance,
        'model_name': model_name,
        'form_title': f'Alterar Status de {instance}',
        'form_action_url': request.path
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('dashboard/partials/quick_status_update_modal.html', context, request=request)
        return HttpResponse(html_form)

    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)
