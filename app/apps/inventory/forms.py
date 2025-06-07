# inventory/forms.py
from django import forms
from .models import Fornecedor, Produto, CategoriaProduto

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = [
            'nome', 'documento', 'telefone', 'email',
            'endereco_logradouro', 'endereco_numero', 'endereco_complemento',
            'endereco_bairro', 'endereco_cidade', 'endereco_estado', 'endereco_cep'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Fornecedor'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ ou CPF'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@fornecedor.com'}),
            'endereco_logradouro': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'endereco_cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
        }

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if documento:
            return "".join(filter(str.isdigit, documento))
        return documento

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            return "".join(filter(str.isdigit, telefone))
        return telefone

    def clean_endereco_cep(self):
        cep = self.cleaned_data.get('endereco_cep')
        if cep:
            return "".join(filter(str.isdigit, cep))
        return cep

class CategoriaProdutoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProduto
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Categoria'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição (opcional)'}),
        }

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome', 'fabricante', 'fornecedor', 'categoria', 'descricao',
            'preco_compra', 'preco_venda_sugerido',
            'codigo_barras', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Produto'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Fabricante'}),
            'fornecedor': forms.Select(attrs={'class': 'form-control custom-select select2-field'}),
            'categoria': forms.Select(attrs={'class': 'form-control custom-select select2-field'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preco_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_venda_sugerido': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'preco_venda_sugerido': 'Preço de Venda (Sug.)',
            'codigo_barras': 'Código de Barras (EAN)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'fornecedor' in self.fields:
            self.fields['fornecedor'].queryset = Fornecedor.objects.order_by('nome')
        if 'categoria' in self.fields:
            self.fields['categoria'].queryset = CategoriaProduto.objects.order_by('nome')
