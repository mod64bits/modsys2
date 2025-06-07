# inventory/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Fornecedor, Produto, CategoriaProduto
from .forms import FornecedorForm, ProdutoForm, CategoriaProdutoForm

# --- Views para Fornecedor ---
@login_required
def fornecedor_list(request):
    fornecedores = Fornecedor.objects.all()
    context = {
        'fornecedores': fornecedores,
        'page_title': 'Lista de Fornecedores'
    }
    return render(request, 'inventory/fornecedor_list.html', context)

@login_required
def fornecedor_create_modal(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            fornecedor = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Fornecedor criado com sucesso!', 'fornecedor_id': fornecedor.pk, 'fornecedor_name': fornecedor.nome})
            messages.success(request, 'Fornecedor criado com sucesso!')
            return redirect('inventory:fornecedor_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao criar fornecedor.')
    else:
        form = FornecedorForm()

    context = {'form': form, 'form_title': 'Novo Fornecedor', 'form_action_url': request.path}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('inventory/partials/fornecedor_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

@login_required
def fornecedor_detail_modal(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    produtos_fornecidos = fornecedor.produtos.all()
    context = {
        'fornecedor': fornecedor,
        'produtos_fornecidos': produtos_fornecidos,
        'detail_title': f'Detalhes do Fornecedor: {fornecedor.nome}'
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('inventory/partials/fornecedor_detail_modal_content.html', context, request=request)
        return HttpResponse(html_content)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

@login_required
def fornecedor_update_modal(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Fornecedor atualizado com sucesso!'})
            messages.success(request, 'Fornecedor atualizado com sucesso!')
            return redirect('inventory:fornecedor_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao atualizar fornecedor.')
    else:
        form = FornecedorForm(instance=fornecedor)

    context = {'form': form, 'fornecedor': fornecedor, 'form_title': f'Editar Fornecedor: {fornecedor.nome}', 'form_action_url': request.path}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('inventory/partials/fornecedor_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

@login_required
def fornecedor_delete_modal(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        fornecedor_name = fornecedor.nome
        try:
            fornecedor.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': f'Fornecedor {fornecedor_name} excluído com sucesso!'})
            messages.success(request, f'Fornecedor {fornecedor_name} excluído com sucesso!')
        except Exception as e:
             if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Erro ao excluir {fornecedor_name}: {str(e)}'}, status=400)
             messages.error(request, f'Erro ao excluir {fornecedor_name}: {str(e)}')
        return redirect('inventory:fornecedor_list')

    context = {'fornecedor': fornecedor, 'delete_title': f'Confirmar Exclusão: {fornecedor.nome}', 'form_action_url': request.path}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('inventory/partials/fornecedor_delete_confirm_modal_content.html', context, request=request)
        return HttpResponse(html_content)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)


# --- Views para Categoria de Produto ---
@login_required
def categoriaproduto_list(request):
    categorias = CategoriaProduto.objects.all()
    context = {
        'categorias': categorias,
        'page_title': 'Categorias de Produtos'
    }
    return render(request, 'inventory/categoriaproduto_list.html', context)

@login_required
def categoriaproduto_create_modal(request):
    if request.method == 'POST':
        form = CategoriaProdutoForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Categoria criada com sucesso!', 'categoria_id': categoria.pk, 'categoria_name': categoria.nome})
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('inventory:categoriaproduto_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao criar categoria.')
    else:
        form = CategoriaProdutoForm()

    context = {'form': form, 'form_title': 'Nova Categoria de Produto', 'form_action_url': request.path}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('inventory/partials/categoriaproduto_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

@login_required
def categoriaproduto_detail_modal(request, pk): # Detalhe de categoria pode ser simples
    categoria = get_object_or_404(CategoriaProduto, pk=pk)
    produtos_na_categoria = categoria.produtos.all()
    context = {
        'categoria': categoria,
        'produtos_na_categoria': produtos_na_categoria,
        'detail_title': f'Detalhes da Categoria: {categoria.nome}'
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('inventory/partials/categoriaproduto_detail_modal_content.html', context, request=request)
        return HttpResponse(html_content)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)


@login_required
def categoriaproduto_update_modal(request, pk):
    categoria = get_object_or_404(CategoriaProduto, pk=pk)
    if request.method == 'POST':
        form = CategoriaProdutoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Categoria atualizada com sucesso!'})
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('inventory:categoriaproduto_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao atualizar categoria.')
    else:
        form = CategoriaProdutoForm(instance=categoria)

    context = {'form': form, 'categoria': categoria, 'form_title': f'Editar Categoria: {categoria.nome}', 'form_action_url': request.path}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('inventory/partials/categoriaproduto_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

@login_required
def categoriaproduto_delete_modal(request, pk):
    categoria = get_object_or_404(CategoriaProduto, pk=pk)
    if request.method == 'POST':
        categoria_name = categoria.nome
        try:
            categoria.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': f'Categoria {categoria_name} excluída com sucesso!'})
            messages.success(request, f'Categoria {categoria_name} excluída com sucesso!')
        except Exception as e:
             if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Erro ao excluir {categoria_name}: {str(e)}'}, status=400)
             messages.error(request, f'Erro ao excluir {categoria_name}: {str(e)}')
        return redirect('inventory:categoriaproduto_list')

    context = {'categoria': categoria, 'delete_title': f'Confirmar Exclusão: {categoria.nome}', 'form_action_url': request.path}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('inventory/partials/categoriaproduto_delete_confirm_modal_content.html', context, request=request)
        return HttpResponse(html_content)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)


# --- Views para Produto ---
@login_required
def produto_list(request):
    produtos = Produto.objects.select_related('fornecedor', 'categoria').all()
    context = {
        'produtos': produtos,
        'page_title': 'Lista de Produtos'
    }
    return render(request, 'inventory/produto_list.html', context)

@login_required
def produto_create_modal(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Produto criado com sucesso!', 'produto_id': produto.pk, 'produto_name': str(produto)})
            messages.success(request, 'Produto criado com sucesso!')
            return redirect('inventory:produto_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao criar produto.')
    else:
        form = ProdutoForm()

    context = {'form': form, 'form_title': 'Novo Produto', 'form_action_url': request.path}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('inventory/partials/produto_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

@login_required
def produto_detail_modal(request, pk):
    produto = get_object_or_404(Produto.objects.select_related('fornecedor', 'categoria'), pk=pk)
    context = {
        'produto': produto,
        'detail_title': f'Detalhes do Produto: {produto.nome}'
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('inventory/partials/produto_detail_modal_content.html', context, request=request)
        return HttpResponse(html_content)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

@login_required
def produto_update_modal(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Produto atualizado com sucesso!'})
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('inventory:produto_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
            messages.error(request, 'Erro ao atualizar produto.')
    else:
        form = ProdutoForm(instance=produto)

    context = {'form': form, 'produto': produto, 'form_title': f'Editar Produto: {produto.nome}', 'form_action_url': request.path}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_form = render_to_string('inventory/partials/produto_form_modal_content.html', context, request=request)
        return HttpResponse(html_form)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)

@login_required
def produto_delete_modal(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto_name = produto.nome
        produto.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Produto {produto_name} excluído com sucesso!'})
        messages.success(request, f'Produto {produto_name} excluído com sucesso!')
        return redirect('inventory:produto_list')

    context = {'produto': produto, 'delete_title': f'Confirmar Exclusão: {produto.nome}', 'form_action_url': request.path}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('inventory/partials/produto_delete_confirm_modal_content.html', context, request=request)
        return HttpResponse(html_content)
    return JsonResponse({'error': 'Acesso direto não permitido.'}, status=403)
