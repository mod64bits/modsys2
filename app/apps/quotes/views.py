# quotes/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string, get_template
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from io import BytesIO
from xhtml2pdf import pisa

from .models import Orcamento, ItemProdutoOrcamento, MaoDeObraOrcamento, InformacoesOrcamento, InsumoOrcamento
from .forms import (
    OrcamentoForm, ItemProdutoOrcamentoFormSet, MaoDeObraOrcamentoFormSet,
    InformacoesOrcamentoForm, InsumoOrcamentoFormSet
)
from apps.servicedesk.models import Ticket, WorkOrder, ProdutoUtilizadoOS
from apps.inventory.models import Produto
from apps.customers.models import Customer

# Função auxiliar para PDF
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

@login_required
def orcamento_list(request):
    orcamentos = Orcamento.objects.select_related('cliente', 'created_by').all()
    context = {
        'orcamentos': orcamentos,
        'page_title': 'Lista de Orçamentos'
    }
    return render(request, 'quotes/orcamento_list.html', context)

@login_required
def orcamento_create_view(request):
    if request.method == 'POST':
        form = OrcamentoForm(request.POST)
        item_produto_formset = ItemProdutoOrcamentoFormSet(request.POST, prefix='itens_produto')
        mao_de_obra_formset = MaoDeObraOrcamentoFormSet(request.POST, prefix='itens_mao_de_obra')
        insumo_formset = InsumoOrcamentoFormSet(request.POST, prefix='insumos')
        informacoes_form = InformacoesOrcamentoForm(request.POST, prefix='informacoes')

        if form.is_valid() and item_produto_formset.is_valid() and \
           mao_de_obra_formset.is_valid() and insumo_formset.is_valid() and informacoes_form.is_valid():

            try:
                with transaction.atomic():
                    orcamento = form.save(commit=False)
                    orcamento.created_by = request.user
                    orcamento.save()
                    informacoes = informacoes_form.save(commit=False)
                    informacoes.orcamento = orcamento
                    informacoes.save()
                    item_produto_formset.instance = orcamento
                    item_produto_formset.save()
                    mao_de_obra_formset.instance = orcamento
                    mao_de_obra_formset.save()
                    insumo_formset.instance = orcamento
                    insumo_formset.save()
                    orcamento.recalcular_totais()
                messages.success(request, 'Orçamento criado com sucesso!')
                return redirect('quotes:orcamento_detail', pk=orcamento.pk)
            except Exception as e:
                messages.error(request, f"Erro ao guardar o orçamento: {e}")
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = OrcamentoForm()
        item_produto_formset = ItemProdutoOrcamentoFormSet(prefix='itens_produto')
        mao_de_obra_formset = MaoDeObraOrcamentoFormSet(prefix='itens_mao_de_obra')
        insumo_formset = InsumoOrcamentoFormSet(prefix='insumos')
        informacoes_form = InformacoesOrcamentoForm(prefix='informacoes')

    context = {
        'form': form, 'item_produto_formset': item_produto_formset,
        'mao_de_obra_formset': mao_de_obra_formset, 'insumo_formset': insumo_formset,
        'informacoes_form': informacoes_form, 'page_title': 'Novo Orçamento',
        'form_action_url': request.path, 'is_create_view': True
    }
    return render(request, 'quotes/orcamento_form.html', context)

@login_required
def orcamento_update_view(request, pk):
    orcamento = get_object_or_404(Orcamento, pk=pk)
    if orcamento.status in [Orcamento.StatusOrcamento.APROVADO, Orcamento.StatusOrcamento.CONCLUIDO, Orcamento.StatusOrcamento.CANCELADO]:
        messages.warning(request, f"Orçamento {orcamento.get_status_display()} não pode ser editado.")
        return redirect('quotes:orcamento_detail', pk=orcamento.pk)

    try:
        informacoes_instance = orcamento.informacoes_adicionais
    except InformacoesOrcamento.DoesNotExist:
        informacoes_instance = None

    if request.method == 'POST':
        form = OrcamentoForm(request.POST, instance=orcamento)
        item_produto_formset = ItemProdutoOrcamentoFormSet(request.POST, instance=orcamento, prefix='itens_produto')
        mao_de_obra_formset = MaoDeObraOrcamentoFormSet(request.POST, instance=orcamento, prefix='itens_mao_de_obra')
        insumo_formset = InsumoOrcamentoFormSet(request.POST, instance=orcamento, prefix='insumos')
        informacoes_form = InformacoesOrcamentoForm(request.POST, instance=informacoes_instance, prefix='informacoes')

        if form.is_valid() and item_produto_formset.is_valid() and \
           mao_de_obra_formset.is_valid() and insumo_formset.is_valid() and informacoes_form.is_valid():

            try:
                with transaction.atomic():
                    orcamento = form.save()
                    informacoes = informacoes_form.save(commit=False)
                    informacoes.orcamento = orcamento
                    informacoes.save()
                    item_produto_formset.save()
                    mao_de_obra_formset.save()
                    insumo_formset.save()
                    orcamento.recalcular_totais()
                messages.success(request, 'Orçamento atualizado com sucesso!')
                return redirect('quotes:orcamento_detail', pk=orcamento.pk)
            except Exception as e:
                messages.error(request, f"Erro ao atualizar o orçamento: {e}")
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = OrcamentoForm(instance=orcamento)
        item_produto_formset = ItemProdutoOrcamentoFormSet(instance=orcamento, prefix='itens_produto')
        mao_de_obra_formset = MaoDeObraOrcamentoFormSet(instance=orcamento, prefix='itens_mao_de_obra')
        insumo_formset = InsumoOrcamentoFormSet(instance=orcamento, prefix='insumos')
        informacoes_form = InformacoesOrcamentoForm(instance=informacoes_instance, prefix='informacoes')

    context = {
        'form': form, 'orcamento': orcamento, 'item_produto_formset': item_produto_formset,
        'mao_de_obra_formset': mao_de_obra_formset, 'insumo_formset': insumo_formset,
        'informacoes_form': informacoes_form, 'page_title': f'Editar Orçamento #{orcamento.pk}',
        'form_action_url': request.path, 'is_create_view': False
    }
    return render(request, 'quotes/orcamento_form.html', context)

@login_required
def orcamento_detail_view(request, pk):
    orcamento = get_object_or_404(Orcamento.objects.select_related(
        'cliente', 'created_by'
    ).prefetch_related(
        'itens_produto__produto', 'itens_mao_de_obra', 'insumos_orcamento'
    ), pk=pk)

    itens_produto = orcamento.itens_produto.all()
    itens_mao_de_obra = orcamento.itens_mao_de_obra.all()
    insumos = orcamento.insumos_orcamento.all()

    try:
        informacoes = orcamento.informacoes_adicionais
    except InformacoesOrcamento.DoesNotExist:
        informacoes = None

    context = {
        'orcamento': orcamento, 'itens_produto': itens_produto,
        'itens_mao_de_obra': itens_mao_de_obra, 'insumos': insumos,
        'informacoes': informacoes, 'page_title': f'Detalhes do Orçamento #{orcamento.pk}'
    }
    return render(request, 'quotes/orcamento_detail.html', context)

@login_required
def orcamento_delete_view(request, pk):
    orcamento = get_object_or_404(Orcamento, pk=pk)
    if request.method == 'POST':
        orcamento_id = orcamento.id
        orcamento.delete()
        messages.success(request, f'Orçamento #{orcamento_id} excluído com sucesso!')
        return redirect('quotes:orcamento_list')

    context = { 'orcamento': orcamento, 'page_title': f'Confirmar Exclusão do Orçamento #{orcamento.pk}' }
    return render(request, 'quotes/orcamento_confirm_delete.html', context)

@login_required
def orcamento_pdf_view(request, pk):
    orcamento = get_object_or_404(Orcamento.objects.select_related(
        'cliente'
    ).prefetch_related(
        'itens_produto__produto', 'itens_mao_de_obra'
    ), pk=pk)

    try:
        informacoes = orcamento.informacoes_adicionais
    except InformacoesOrcamento.DoesNotExist:
        informacoes = None

    context = { 'orcamento': orcamento, 'informacoes': informacoes, 'company_name': 'Nome da Sua Empresa Aqui', 'for_client': True }
    pdf = render_to_pdf('quotes/pdf/orcamento_pdf_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Orcamento_{orcamento.pk}_{orcamento.cliente.nome.replace(' ','_')}.pdf"
        content = f"inline; filename=\"{filename}\""
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Erro ao gerar PDF do orçamento.", status=500)

@login_required
def get_product_details_json(request, product_id):
    try:
        produto = Produto.objects.get(pk=product_id)
        data = { 'success': True, 'preco_compra': str(produto.preco_compra), 'preco_venda_sugerido': str(produto.preco_venda_sugerido) if produto.preco_venda_sugerido else '', 'nome_produto_selecionado': str(produto) }
        return JsonResponse(data)
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produto não encontrado.'}, status=404)

@login_required
def generate_os_from_quote(request, pk):
    orcamento = get_object_or_404(Orcamento, pk=pk)

    if orcamento.status != 'APROVADO':
        messages.error(request, "Apenas orçamentos aprovados podem ser convertidos em Ordem de Serviço.")
        return redirect('quotes:orcamento_detail', pk=orcamento.pk)

    try:
        with transaction.atomic():
            # 1. Criar um novo Ticket
            novo_ticket = Ticket.objects.create(
                title=f"Serviços referentes ao Orçamento #{orcamento.pk}",
                description=f"Execução dos serviços e fornecimento de produtos conforme Orçamento Aprovado nº {orcamento.pk}.\n\nDescrição Geral: {orcamento.descricao_geral or 'N/A'}",
                customer=orcamento.cliente,
                created_by=request.user,
                status='EM_ANDAMENTO',
                priority='MEDIA'
            )

            # 2. Criar uma Ordem de Serviço principal
            servicos_descricao = []
            for item_mao_obra in orcamento.itens_mao_de_obra.all():
                servicos_descricao.append(f"- {item_mao_obra.get_tipo_display()}: {item_mao_obra.descricao}")

            nova_os = WorkOrder.objects.create(
                ticket=novo_ticket,
                orcamento_origem=orcamento,
                description="\n".join(servicos_descricao) or "Executar serviços conforme orçamento.",
                status='PENDENTE'
            )

            # 3. Vincular produtos à nova OS e abater do stock
            for item_produto in orcamento.itens_produto.all():
                produto = item_produto.produto
                if produto.quantidade_em_estoque < item_produto.quantidade:
                    raise Exception(f"Stock insuficiente para o produto '{produto.nome}'. Necessário: {item_produto.quantidade}, Disponível: {produto.quantidade_em_estoque}.")

                ProdutoUtilizadoOS.objects.create(
                    ordem_de_servico=nova_os,
                    produto=produto,
                    quantidade=item_produto.quantidade,
                    preco_compra_no_momento=item_produto.preco_compra_unitario_historico,
                    preco_venda_no_momento=item_produto.get_preco_venda_unitario_calculado()
                )
                # O signal em servicedesk.models irá tratar de abater o stock

            # 4. Atualizar o status do orçamento
            orcamento.status = 'CONCLUIDO'
            orcamento.save()

        messages.success(request, f"Ordem de Serviço #{nova_os.id} e Ticket #{novo_ticket.id} gerados com sucesso a partir do orçamento!")
        return redirect('servicedesk:work_order_list') # Redireciona para a lista de OS

    except Exception as e:
        messages.error(request, f"Erro ao gerar a Ordem de Serviço: {e}")
        return redirect('quotes:orcamento_detail', pk=orcamento.pk)
