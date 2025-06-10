# dashboard/forms.py
from django import forms
from apps.servicedesk.models import Ticket, WorkOrder
from apps.quotes.models import Orcamento # Importar Orçamento

class QuickTicketStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control custom-select'}),
        }
        labels = {
            'status': 'Novo Status do Ticket'
        }

class QuickWorkOrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control custom-select'}),
        }
        labels = {
            'status': 'Novo Status da Ordem de Serviço'
        }

# Novo Formulário para o Status do Orçamento
class QuickOrcamentoStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control custom-select'}),
        }
        labels = {
            'status': 'Novo Status do Orçamento'
        }

