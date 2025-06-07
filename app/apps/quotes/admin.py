# quotes/admin.py
from django.contrib import admin

from .forms import ItemProdutoOrcamentoForm, MaoDeObraOrcamentoForm, InsumoOrcamentoForm, InformacoesOrcamentoForm
from .models import Orcamento, ItemProdutoOrcamento, MaoDeObraOrcamento, InformacoesOrcamento, InsumoOrcamento

class ItemProdutoOrcamentoInline(admin.TabularInline):
    model = ItemProdutoOrcamento
    form = ItemProdutoOrcamentoForm # Usar o form customizado se precisar de lógica extra
    extra = 1
    fields = ('produto_lookup', 'produto', 'quantidade', 'preco_compra_unitario_historico', 'preco_venda_unitario_definido', 'porcentagem_markup')
    readonly_fields = ('preco_compra_unitario_historico',) # Preenchido no save do item
    # Adicionar JS para popular 'produto' e 'preco_compra_unitario_historico' a partir do 'produto_lookup'
    # class Media:
    #     js = ('js/admin_orcamento_item_produto.js',) # Exemplo

class MaoDeObraOrcamentoInline(admin.TabularInline):
    model = MaoDeObraOrcamento
    form = MaoDeObraOrcamentoForm
    extra = 1

class InsumoOrcamentoInline(admin.TabularInline):
    model = InsumoOrcamento
    form = InsumoOrcamentoForm
    extra = 1

class InformacoesOrcamentoInline(admin.StackedInline): # Ou TabularInline
    model = InformacoesOrcamento
    form = InformacoesOrcamentoForm
    can_delete = False # Geralmente não se deleta, apenas se edita

@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cliente', 'status', 'validade',
        'valor_total_orcamento', 'lucro_total_liquido',
        'created_by', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'cliente', 'created_at', 'validade', 'created_by')
    search_fields = ('id', 'cliente__nome', 'descricao_geral', 'created_by__username')
    readonly_fields = (
        'total_produtos_compra', 'total_produtos_venda', 'total_mao_de_obra',
        'total_insumos', 'valor_total_orcamento', 'lucro_equipamentos',
        'lucro_total_bruto', 'lucro_total_liquido',
        'created_at', 'updated_at', 'created_by'
    )
    fieldsets = (
        (None, {
            'fields': ('cliente', ('status', 'validade'), 'descricao_geral')
        }),
        ("Valores Calculados (Somente Leitura)", {
            'fields': (
                ('total_produtos_compra', 'total_produtos_venda', 'lucro_equipamentos'),
                ('total_mao_de_obra', 'total_insumos'),
                ('valor_total_orcamento', 'lucro_total_bruto', 'lucro_total_liquido'),
            ),
            'classes': ('collapse',)
        }),
        ("Controle", {
            'fields': ('created_by', 'created_at', 'updated_at')
        })
    )
    inlines = [
        ItemProdutoOrcamentoInline,
        MaoDeObraOrcamentoInline,
        InsumoOrcamentoInline,
        InformacoesOrcamentoInline,
    ]

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Ao criar um novo orçamento
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        # Após salvar o modelo e os inlines, recalcular os totais
        obj.recalcular_totais()

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        # Após salvar o formset (itens), recalcular os totais do orçamento principal
        # O 'instance' do formset é o objeto Orcamento
        if formset.instance and formset.instance.pk:
            formset.instance.recalcular_totais()

# Opcional: registrar os modelos de item separadamente se precisar de gerenciamento direto
# @admin.register(ItemProdutoOrcamento)
# class ItemProdutoOrcamentoAdmin(admin.ModelAdmin):
#     list_display = ('orcamento', 'produto', 'quantidade', 'preco_venda_unitario_definido')

# @admin.register(MaoDeObraOrcamento)
# class MaoDeObraOrcamentoAdmin(admin.ModelAdmin):
#     list_display = ('orcamento', 'descricao', 'tipo', 'valor')

# @admin.register(InsumoOrcamento)
# class InsumoOrcamentoAdmin(admin.ModelAdmin):
#     list_display = ('orcamento', 'descricao', 'valor', 'data_gasto')
