# quotes/forms.py
from django import forms
from django.forms import inlineformset_factory, NumberInput
from django.utils.translation import gettext_lazy as _
from .models import Orcamento, ItemProdutoOrcamento, MaoDeObraOrcamento, InformacoesOrcamento, InsumoOrcamento
from apps.customers.models import Customer
from apps.inventory.models import Produto
from decimal import Decimal

class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ['cliente', 'validade', 'status', 'descricao_geral']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control custom-select select2-field'}),
            'validade': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}), # Formato adicionado
            'status': forms.Select(attrs={'class': 'form-control custom-select'}),
            'descricao_geral': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações gerais sobre o orçamento...'}),
        }
        labels = {
            'descricao_geral': _('Descrição Geral / Observações'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Customer.objects.order_by('nome')


class ItemProdutoOrcamentoForm(forms.ModelForm):
    produto_lookup = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True).order_by('nome'),
        label=_("Buscar Produto"),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control custom-select select2-field product-lookup', 'data-placeholder': 'Selecione ou busque um produto...'})
    )

    class Meta:
        model = ItemProdutoOrcamento
        fields = [
            'produto', 'quantidade', 'preco_compra_unitario_historico',
            'preco_venda_unitario_definido', 'porcentagem_markup'
        ]
        widgets = {
            'produto': forms.HiddenInput(),
            'quantidade': NumberInput(attrs={'class': 'form-control item-calc', 'step': '0.01', 'min':'0.01'}),
            'preco_compra_unitario_historico': NumberInput(attrs={'class': 'form-control item-calc product-cost-price', 'step': '0.01', 'readonly':'readonly'}),
            'preco_venda_unitario_definido': NumberInput(attrs={'class': 'form-control item-calc product-sell-price', 'step': '0.01'}),
            'porcentagem_markup': NumberInput(attrs={'class': 'form-control item-calc product-markup', 'step': '0.01', 'placeholder': '% Markup'}),
        }
        labels = {
            'preco_compra_unitario_historico': _('Custo Unit. (Automático)'),
            'preco_venda_unitario_definido': _('Venda Unit.'),
            'porcentagem_markup': _('Markup (%)'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.produto:
             self.fields['produto_lookup'].initial = self.instance.produto


class MaoDeObraOrcamentoForm(forms.ModelForm):
    class Meta:
        model = MaoDeObraOrcamento
        fields = ['tipo', 'descricao', 'valor']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control custom-select'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição do serviço de mão de obra'}),
            'valor': NumberInput(attrs={'class': 'form-control item-calc', 'step': '0.01'}),
        }

class InformacoesOrcamentoForm(forms.ModelForm):
    class Meta:
        model = InformacoesOrcamento
        fields = ['condicoes_pagamento', 'prazo_entrega_instalacao', 'garantia']
        widgets = {
            'condicoes_pagamento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prazo_entrega_instalacao': forms.TextInput(attrs={'class': 'form-control'}),
            'garantia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InsumoOrcamentoForm(forms.ModelForm):
    class Meta:
        model = InsumoOrcamento
        fields = ['descricao', 'valor', 'data_gasto']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição do insumo ou gasto'}),
            'valor': NumberInput(attrs={'class': 'form-control item-calc', 'step': '0.01'}),
            'data_gasto': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}), # Formato adicionado
        }

ItemProdutoOrcamentoFormSet = inlineformset_factory(
    Orcamento, ItemProdutoOrcamento, form=ItemProdutoOrcamentoForm,
    extra=1, can_delete=True, can_delete_extra=True
)

MaoDeObraOrcamentoFormSet = inlineformset_factory(
    Orcamento, MaoDeObraOrcamento, form=MaoDeObraOrcamentoForm,
    extra=1, can_delete=True, can_delete_extra=True
)

InsumoOrcamentoFormSet = inlineformset_factory(
    Orcamento, InsumoOrcamento, form=InsumoOrcamentoForm,
    extra=1, can_delete=True, can_delete_extra=True
)
