# financial/views.py
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string


from .models import ContaReceber, Pagamento
from apps.quotes.models import Orcamento
from .forms import PagamentoForm, ContaReceberForm

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

