# servicedesk/forms.py
from django import forms
from .models import Ticket, WorkOrder
from apps.customers.models import Customer # Importar o modelo Customer

class TicketForm(forms.ModelForm):
    # Adicionar o campo customer ao formulário
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False, # Defina como True se um cliente for sempre obrigatório
        widget=forms.Select(attrs={'class': 'form-control custom-select'}),
        label="Cliente"
    )

    class Meta:
        model = Ticket
        # Adicionar 'customer' aos fields
        fields = ['title', 'customer', 'description', 'priority', 'status', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título breve do problema'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Descreva o problema detalhadamente'}),
            'priority': forms.Select(attrs={'class': 'form-control custom-select'}),
            'status': forms.Select(attrs={'class': 'form-control custom-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control custom-select'}),
            # 'category': forms.Select(attrs={'class': 'form-control custom-select'}), # Se você tiver categorias
        }
        labels = {
            'title': 'Título do Ticket',
            'description': 'Descrição Detalhada',
            'priority': 'Prioridade',
            'status': 'Status',
            'assigned_to': 'Atribuir Para',
            # 'category': 'Categoria',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # O campo 'customer' já foi definido acima, então não precisa de manipulação especial aqui
        # a menos que você queira filtrar o queryset de clientes com base no usuário, por exemplo.


class WorkOrderForm(forms.ModelForm):
    # Se quiser adicionar cliente diretamente à OS, embora já venha do ticket:
    # customer = forms.ModelChoiceField(
    #     queryset=Customer.objects.all(),
    #     required=False,
    #     widget=forms.Select(attrs={'class': 'form-control custom-select select2'}), # Adicionar select2 se usado
    #     label="Cliente da OS"
    # )
    # No entanto, vamos manter a OS vinculada ao cliente do ticket por enquanto.

    class Meta:
        model = WorkOrder
        fields = ['ticket', 'description', 'status', 'assigned_technician', 'scheduled_date', 'notes']
        widgets = {
            'ticket': forms.Select(attrs={'class': 'form-control custom-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição dos serviços a serem realizados'}),
            'status': forms.Select(attrs={'class': 'form-control custom-select'}),
            'assigned_technician': forms.Select(attrs={'class': 'form-control custom-select'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações internas sobre a OS'}),
        }
        labels = {
            'ticket': 'Ticket Relacionado',
            'description': 'Descrição da OS',
            'status': 'Status da OS',
            'assigned_technician': 'Técnico Responsável',
            'scheduled_date': 'Data Agendada',
            'notes': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra tickets para mostrar apenas os que não estão fechados ou resolvidos.
        self.fields['ticket'].queryset = Ticket.objects.exclude(status__in=['FECHADO', 'RESOLVIDO'])
