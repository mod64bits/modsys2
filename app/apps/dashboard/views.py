# dashboard/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, ExtractYear
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from calendar import month_name

from apps.servicedesk.models import Ticket, WorkOrder
from apps.quotes.models import Orcamento
from .forms import QuickTicketStatusUpdateForm, QuickWorkOrderStatusUpdateForm, QuickOrcamentoStatusUpdateForm

@login_required
def dashboard_view(request):
    """
    Renderiza a página principal do dashboard.
    """
    end_date = timezone.now()
    start_date_activities = end_date - timedelta(days=30)
    start_date_billing = end_date.replace(month=1, day=1)

    # Obter anos distintos para preencher o filtro de faturamento
    available_years = Orcamento.objects.annotate(
        year=ExtractYear('created_at')
    ).values_list('year', flat=True).distinct().order_by('-year')

    current_year = end_date.year
    previous_year = current_year - 1

    recent_open_tickets = Ticket.objects.filter(
        status__in=['ABERTO', 'EM_ANDAMENTO']
    ).select_related('customer').order_by('-created_at')[:10]

    recent_open_work_orders = WorkOrder.objects.filter(
        status__in=['PENDENTE', 'EM_EXECUCAO', 'AGENDADA']
    ).select_related('ticket__customer').order_by('-created_at')[:10]

    recent_pending_quotes = Orcamento.objects.exclude(
        status__in=['APROVADO', 'REPROVADO', 'CONCLUIDO', 'CANCELADO']
    ).select_related('cliente').order_by('-created_at')[:10]

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
def dashboard_data_api(request):
    """
    API AJAX que retorna dados para os gráficos.
    """
    data_type = request.GET.get('data_type', 'all')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    data = {}

    try:
        start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        end_date_obj = timezone.now()
        start_date_obj = end_date_obj - timedelta(days=30)
        start_date = start_date_obj.date()
        end_date = end_date_obj.date()

    end_date_for_query = end_date + timedelta(days=1)

    if data_type == 'activities':
        tickets_por_status = Ticket.objects.filter(
            created_at__gte=start_date, created_at__lt=end_date_for_query
        ).values('status').annotate(count=Count('id')).order_by('status')

        os_por_status = WorkOrder.objects.filter(
            created_at__gte=start_date, created_at__lt=end_date_for_query
        ).values('status').annotate(count=Count('id')).order_by('status')

        data['tickets_por_status'] = list(tickets_por_status)
        data['os_por_status'] = list(os_por_status)

    if data_type == 'billing':
        year1_str = request.GET.get('year1')
        year2_str = request.GET.get('year2')

        try:
            year1 = int(year1_str) if year1_str else timezone.now().year
            year2 = int(year2_str) if year2_str and year2_str != '' else 0
        except (ValueError, TypeError):
            year1 = timezone.now().year
            year2 = 0

        faturamento_total_periodo = Orcamento.objects.filter(
            status='APROVADO', created_at__year=year1
        ).aggregate(total=Sum('valor_total_orcamento'))['total'] or 0

        vendas_ano_1 = Orcamento.objects.filter(
            status='APROVADO', created_at__year=year1
        ).annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('valor_total_orcamento')).order_by('month')

        labels_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        dados_ano_1 = [0] * 12
        dados_ano_2 = [0] * 12

        for venda in vendas_ano_1:
            dados_ano_1[venda['month'].month - 1] = float(venda['total'])

        if year2 > 0:
            vendas_ano_2_query = Orcamento.objects.filter(
                status='APROVADO', created_at__year=year2
            ).annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('valor_total_orcamento')).order_by('month')
            for venda in vendas_ano_2_query:
                dados_ano_2[venda['month'].month - 1] = float(venda['total'])

        data['faturamento_ao_longo_do_tempo'] = {
            'total_geral': float(faturamento_total_periodo),
            'labels': labels_meses,
            'ano1': {'label': str(year1), 'data': dados_ano_1},
            'ano2': {'label': str(year2), 'data': dados_ano_2}
        }

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
