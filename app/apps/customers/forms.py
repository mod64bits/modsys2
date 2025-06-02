# customers/forms.py
from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'nome', 'tipo_documento', 'documento', 'telefone', 'email',
            'tipo_cliente',
            'endereco_logradouro', 'endereco_numero', 'endereco_complemento',
            'endereco_bairro', 'endereco_cidade', 'endereco_estado', 'endereco_cep',
            'criar_usuario_sistema' # Campo para decidir se cria usuário
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Completo ou Razão Social'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control custom-select'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF ou CNPJ'}), # JS para máscara
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}), # JS para máscara
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'tipo_cliente': forms.Select(attrs={'class': 'form-control custom-select'}),
            'endereco_logradouro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua, Avenida, etc.'}),
            'endereco_numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nº'}),
            'endereco_complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apto, Bloco, Sala'}),
            'endereco_bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'endereco_cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'endereco_estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF (ex: SP)'}),
            'endereco_cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}), # JS para máscara
            'criar_usuario_sistema': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome': 'Nome / Razão Social',
            'documento': 'CPF/CNPJ',
            'endereco_logradouro': 'Logradouro',
            'endereco_numero': 'Número',
            'endereco_complemento': 'Complemento',
            'endereco_bairro': 'Bairro',
            'endereco_cidade': 'Cidade',
            'endereco_estado': 'UF',
            'endereco_cep': 'CEP',
            'criar_usuario_sistema': 'Criar usuário de acesso ao sistema para este cliente?',
        }

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        # Aqui você pode adicionar validações específicas para CPF/CNPJ se desejar,
        # usando bibliotecas como 'validate_docbr'
        # Por enquanto, apenas removemos caracteres não numéricos para consistência,
        # mas a validação real do formato/dígitos verificadores seria mais robusta.
        if documento:
            documento = "".join(filter(str.isdigit, documento))
        return documento

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            telefone = "".join(filter(str.isdigit, telefone))
        return telefone

    def clean_cep(self): # Renomeado de clean_endereco_cep para clean_cep
        cep = self.cleaned_data.get('endereco_cep') # Corrigido para pegar 'endereco_cep'
        if cep:
            cep = "".join(filter(str.isdigit, cep))
        return cep

