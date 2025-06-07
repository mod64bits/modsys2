# reports/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from io import BytesIO
from xhtml2pdf import pisa

from .forms import ReportFilterForm
from apps.servicedesk.models import Ticket, WorkOrder
from apps.customers.models import Customer # Necessário se for filtrar por cliente

# Função auxiliar para renderizar PDF (pode ser movida para um utils.py)
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    # Encoding UTF-8 é importante para caracteres especiais
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def report_filter_view(request):
    form = ReportFilterForm(request.GET or None)
    tickets_results = Ticket.objects.none() # Queryset vazio por padrão
    work_orders_results = WorkOrder.objects.none() # Queryset vazio por padrão
    show_results = False

    if form.is_valid():
        show_results = True
        customer = form.cleaned_data.get('customer')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        content_type = form.cleaned_data.get('content_type')

        # Ajustar end_date para incluir o dia inteiro
        if end_date:
            end_date_adjusted = end_date + timezone.timedelta(days=1)
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
                # Filtrar OS pelo cliente do ticket associado
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
    # Os filtros são passados via GET params
    form = ReportFilterForm(request.GET or None)
    tickets_results = Ticket.objects.none()
    work_orders_results = WorkOrder.objects.none()

    # Variáveis para o template PDF
    customer_filter = None
    start_date_filter = None
    end_date_filter = None
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
            end_date_adjusted = end_date + timezone.timedelta(days=1)
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
    else:
        # Se o formulário não for válido (ex: acesso direto à URL do PDF sem params),
        # pode-se retornar um erro ou um PDF vazio/padrão.
        # Por ora, vai gerar com o que tiver (provavelmente tudo ou nada).
        # Melhor seria validar e exigir os parâmetros.
        pass


    context = {
        'tickets_results': tickets_results,
        'work_orders_results': work_orders_results,
        'customer_filter': customer_filter,
        'start_date_filter': start_date_filter,
        'end_date_filter': end_date_filter,
        'content_type_filter': content_type_filter,
        'company_name': 'mod64bits', # Ajuste conforme necessário
        'report_date': timezone.now(),
    }

    pdf = render_to_pdf('reports/pdf/filtered_report_pdf_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Relatorio_Filtrado_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        # content = f"inline; filename='{filename}'" # Para exibir no navegador
        content = f"attachment; filename='{filename}'" # Para forçar download
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Erro ao gerar PDF do relatório.", status=500)

