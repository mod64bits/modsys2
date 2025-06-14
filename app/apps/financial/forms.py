# financial/forms.py
from django import forms
from .models import ContaReceber, Pagamento

class ContaReceberForm(forms.ModelForm):
    class Meta:
        model = ContaReceber
        fields = ['cliente', 'orcamento_origem', 'descricao', 'valor_total', 'data_vencimento', 'status']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'orcamento_origem': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_vencimento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['valor_pago', 'data_pagamento', 'metodo', 'observacoes']
        widgets = {
            'valor_pago': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0,00'}),
            'data_pagamento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'metodo': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
