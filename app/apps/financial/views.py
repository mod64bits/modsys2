# financial/views.py
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.template.loader import render_to_string, get_template
from io import BytesIO
from xhtml2pdf import pisa

from .models import ContaReceber, Pagamento
from apps.quotes.models import Orcamento
from .forms import PagamentoForm, ContaReceberForm


# --- Função Auxiliar para PDF ---
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


@login_required
def contareceber_list(request):
    contas = ContaReceber.objects.select_related('cliente', 'orcamento_origem').all()
    context = {
        'contas': contas,
        'page_title': "Contas a Receber"
    }
    return render(request, 'financial/contareceber_list.html', context)

@login_required
def contareceber_detail(request, pk):
    conta = get_object_or_404(ContaReceber, pk=pk)
    pagamentos = conta.pagamentos.all()
    context = {
        'conta': conta,
        'pagamentos': pagamentos,
        'page_title': f"Detalhes da Fatura #{conta.pk}"
    }
    return render(request, 'financial/contareceber_detail.html', context)

@login_required
def add_payment_modal(request, pk):
    conta = get_object_or_404(ContaReceber, pk=pk)
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            pagamento = form.save(commit=False)
            pagamento.conta = conta
            pagamento.registrado_por = request.user
            pagamento.save() # O signal irá atualizar a conta
            return JsonResponse({'success': True, 'message': 'Pagamento registado com sucesso!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = PagamentoForm(initial={'valor_pago': conta.saldo_devedor}) # Sugere o valor restante

    context = {
        'form': form,
        'conta': conta,
        'form_title': f'Adicionar Pagamento à Fatura #{conta.pk}',
        'form_action_url': request.path
    }
    html_form = render_to_string('financial/partials/add_payment_modal.html', context, request=request)
    return HttpResponse(html_form)

@login_required
def generate_conta_from_orcamento(request, orcamento_pk):
    orcamento = get_object_or_404(Orcamento, pk=orcamento_pk)

    if orcamento.status != 'APROVADO':
        messages.error(request, "Apenas orçamentos aprovados podem ser faturados.")
        return redirect('quotes:orcamento_detail', pk=orcamento.pk)

    if hasattr(orcamento, 'conta_a_receber'):
        messages.warning(request, f"Este orçamento já possui uma fatura associada (Fatura #{orcamento.conta_a_receber.pk}).")
        return redirect('financial:contareceber_detail', pk=orcamento.conta_a_receber.pk)

    if request.method == 'POST':
        # Cria a conta a receber
        nova_conta = ContaReceber.objects.create(
            cliente=orcamento.cliente,
            orcamento_origem=orcamento,
            descricao=f"Fatura referente ao Orçamento #{orcamento.pk}",
            valor_total=orcamento.valor_total_orcamento,
            data_vencimento=timezone.now().date() + timedelta(days=30) # Vencimento em 30 dias (exemplo)
        )
        messages.success(request, f"Fatura #{nova_conta.pk} gerada com sucesso!")
        return redirect('financial:contareceber_detail', pk=nova_conta.pk)

    # Se for GET, poderia mostrar uma página de confirmação, mas um POST direto do botão é mais simples.
    return redirect('quotes:orcamento_detail', pk=orcamento.pk)


@login_required
def contareceber_receipt_pdf_view(request, pk):
    """
    Gera um PDF de recibo para uma Conta a Receber, mostrando os pagamentos e o saldo.
    """
    conta = get_object_or_404(ContaReceber.objects.select_related('cliente'), pk=pk)
    pagamentos = conta.pagamentos.all().order_by('data_pagamento')

    context = {
        'conta': conta,
        'pagamentos': pagamentos,
        'company_name': 'Nome da Sua Empresa Aqui', # Ajuste conforme necessário
        'generation_date': timezone.now(),
    }

    pdf = render_to_pdf('financial/pdf/receipt_pdf_template.html', context)

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Recibo_Fatura_{conta.pk}.pdf"
        # Usar aspas duplas para o nome do ficheiro
        content = f"inline; filename={filename}"
        response['Content-Disposition'] = content
        return response

    return HttpResponse("Erro ao gerar o recibo em PDF.", status=500)

