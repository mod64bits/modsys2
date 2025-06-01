# servicedesk/forms.py
from django import forms
from .models import Ticket, WorkOrder

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'status', 'assigned_to'] # Adicione 'category' se usar
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título breve do problema'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Descreva o problema detalhadamente'}),
            'priority': forms.Select(attrs={'class': 'form-control custom-select'}),
            'status': forms.Select(attrs={'class': 'form-control custom-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control custom-select'}),
            'category': forms.Select(attrs={'class': 'form-control custom-select'}),
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
        user = kwargs.pop('user', None) # Para potencialmente filtrar usuários ou definir 'created_by'
        super().__init__(*args, **kwargs)
        # Exemplo: Limitar opções de 'assigned_to' para usuários que são técnicos
        # if user and hasattr(user, 'userprofile') and user.userprofile.is_technician:
        #     self.fields['assigned_to'].queryset = User.objects.filter(userprofile__is_technician=True)
        # else:
        #     self.fields['assigned_to'].queryset = User.objects.all() # Ou alguma outra lógica

        # Se o campo 'created_by' fosse editável (geralmente não é no form, é pego da request.user):
        if user:
            self.instance.created_by = user


class WorkOrderForm(forms.ModelForm):
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
        # Você pode querer filtrar o queryset de 'ticket' para apenas tickets abertos ou algo assim
        # self.fields['ticket'].queryset = Ticket.objects.filter(status__in=['ABERTO', 'EM_ANDAMENTO'])
