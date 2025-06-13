# reports/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from datetime import timedelta
from io import BytesIO
from xhtml2pdf import pisa
from django.db.models import Prefetch # Importar Prefetch

from .forms import ReportFilterForm
from apps.servicedesk.models import Ticket, WorkOrder, TicketComment # Importar TicketComment
from apps.customers.models import Customer

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def report_filter_view(request):
    # A lógica desta view para exibir a pré-visualização na página HTML permanece a mesma.
    # Se também quiser exibir os comentários aqui, a mesma lógica de prefetch deve ser aplicada.
    # ... (código existente da sua view) ...
    form = ReportFilterForm(request.GET or None)
    tickets_results = Ticket.objects.none()
    work_orders_results = WorkOrder.objects.none()
    show_results = False

    if form.is_valid():
        show_results = True
        customer = form.cleaned_data.get('customer')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        content_type = form.cleaned_data.get('content_type')

        if end_date:
            end_date_adjusted = end_date + timedelta(days=1)
        else:
            end_date_adjusted = None

        if content_type == 'tickets_only' or content_type == 'all':
            tickets_query = Ticket.objects.all()
            if customer:
                tickets_query = tickets_query.filter(customer=customer)
            if start_date:
                tickets_query = tickets_query.filter(created_at__gte=start_date)
            if end_date_adjusted:
                tickets_query = tickets_query.filter(created_at__lt=end_date_adjusted)
            tickets_results = tickets_query.order_by('-created_at')

        if content_type == 'work_orders_only' or content_type == 'all':
            work_orders_query = WorkOrder.objects.all()
            if customer:
                work_orders_query = work_orders_query.filter(ticket__customer=customer)
            if start_date:
                work_orders_query = work_orders_query.filter(created_at__gte=start_date)
            if end_date_adjusted:
                work_orders_query = work_orders_query.filter(created_at__lt=end_date_adjusted)
            work_orders_results = work_orders_query.order_by('-created_at')

    context = {
        'form': form,
        'tickets_results': tickets_results,
        'work_orders_results': work_orders_results,
        'show_results': show_results,
        'page_title': 'Relatório Filtrado'
    }
    return render(request, 'reports/report_filter_page.html', context)


def generate_filtered_pdf_view(request):
    form = ReportFilterForm(request.GET or None)
    tickets_results = Ticket.objects.none()
    work_orders_results = WorkOrder.objects.none()

    customer_filter, start_date_filter, end_date_filter = None, None, None
    content_type_filter = 'all'

    if form.is_valid():
        customer = form.cleaned_data.get('customer')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        content_type = form.cleaned_data.get('content_type')

        customer_filter = customer
        start_date_filter = start_date
        end_date_filter = end_date
        content_type_filter = content_type

        if end_date:
            end_date_adjusted = end_date + timedelta(days=1)
        else:
            end_date_adjusted = None

        if content_type == 'tickets_only' or content_type == 'all':
            # CORREÇÃO: Adicionar prefetch para os comentários públicos
            prefetch_comments = Prefetch(
                'comments',
                queryset=TicketComment.objects.filter(
                    is_internal_note=False,
                    comment_type=TicketComment.CommentType.COMMENT
                ).select_related('author').order_by('created_at'),
                to_attr='public_comments' # Armazenar os resultados num novo atributo
            )

            tickets_query = Ticket.objects.select_related('customer').prefetch_related(prefetch_comments)

            if customer:
                tickets_query = tickets_query.filter(customer=customer)
            if start_date:
                tickets_query = tickets_query.filter(created_at__gte=start_date)
            if end_date_adjusted:
                tickets_query = tickets_query.filter(created_at__lt=end_date_adjusted)

            tickets_results = tickets_query.order_by('created_at') # Ordenar por mais antigo para o histórico fazer sentido

        if content_type == 'work_orders_only' or content_type == 'all':
            work_orders_query = WorkOrder.objects.select_related('ticket__customer').all() # Otimização
            if customer:
                work_orders_query = work_orders_query.filter(ticket__customer=customer)
            if start_date:
                work_orders_query = work_orders_query.filter(created_at__gte=start_date)
            if end_date_adjusted:
                work_orders_query = work_orders_query.filter(created_at__lt=end_date_adjusted)
            work_orders_results = work_orders_query.order_by('created_at')

    context = {
        'tickets_results': tickets_results,
        'work_orders_results': work_orders_results,
        'customer_filter': customer_filter,
        'start_date_filter': start_date_filter,
        'end_date_filter': end_date_filter,
        'content_type_filter': content_type_filter,
        'company_name': 'mod64bits',
        'report_date': timezone.now(),
    }

    pdf = render_to_pdf('reports/pdf/filtered_report_pdf_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Relatorio_Filtrado_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Erro ao gerar PDF do relatório.", status=500)
