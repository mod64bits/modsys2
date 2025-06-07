# inventory/admin.py
from django.contrib import admin
from .models import Fornecedor, Produto, CategoriaProduto

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'documento', 'telefone', 'email', 'endereco_cidade', 'updated_at')
    search_fields = ('nome', 'documento', 'email', 'telefone')
    list_filter = ('endereco_estado', 'created_at')
    fieldsets = (
        ("Informações de Contato", {
            'fields': ('nome', 'documento', 'telefone', 'email')
        }),
        ("Endereço", {
            'fields': ('endereco_logradouro', 'endereco_numero', 'endereco_complemento', 'endereco_bairro', 'endereco_cidade', 'endereco_estado', 'endereco_cep'),
            'classes': ('collapse',)
        }),
        ("Datas de Controle", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        })
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CategoriaProduto)
class CategoriaProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'fabricante', 'fornecedor', 'preco_compra', 'preco_venda_sugerido', 'ativo', 'updated_at')
    search_fields = ('nome', 'fabricante', 'fornecedor__nome', 'categoria__nome', 'codigo_barras')
    list_filter = ('ativo', 'categoria', 'fornecedor', 'created_at')
    autocomplete_fields = ['fornecedor', 'categoria']
    fieldsets = (
        (None, {
            'fields': ('nome', 'fabricante', 'descricao', 'ativo')
        }),
        ("Fornecedor & Categoria", {
            'fields': ('fornecedor', 'categoria')
        }),
        ("Precificação", {
            'fields': ('preco_compra', 'preco_venda_sugerido')
        }),
        ("Identificação", {
            'fields': ('codigo_barras',),
        }),
        ("Datas de Controle", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        })
    )
    readonly_fields = ('created_at', 'updated_at')
