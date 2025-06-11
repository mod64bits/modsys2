# servicedesk/forms.py
from django import forms
from .models import Ticket, WorkOrder, TicketComment, Category
from apps.customers.models import Customer

# Novas classes para suportar o upload de múltiplos ficheiros
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        # Define o widget padrão e garante que o atributo HTML 'multiple' esteja presente
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            # Se forem recebidos múltiplos ficheiros, limpa cada um individualmente
            result = [single_file_clean(d, initial) for d in data]
        else:
            # Se for apenas um ficheiro, usa a lógica de limpeza padrão
            result = single_file_clean(data, initial)
        return result

class TicketForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control custom-select'}),
        label="Cliente"
    )
    # Garante que o campo de categoria use o modelo correto
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control custom-select'}),
        label="Categoria"
    )

    class Meta:
        model = Ticket
        fields = ['title', 'customer', 'category', 'description', 'priority', 'status', 'assigned_to'] # Adicionado category
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título breve do problema'}),
            # 'category' é definido acima para garantir o queryset correto
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Descreva o problema detalhadamente'}),
            'priority': forms.Select(attrs={'class': 'form-control custom-select'}),
            'status': forms.Select(attrs={'class': 'form-control custom-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control custom-select'}),
        }
        labels = {
            'title': 'Título do Ticket',
            'description': 'Descrição Detalhada',
            'priority': 'Prioridade',
            'status': 'Status',
            'assigned_to': 'Atribuir Para',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['ticket', 'description', 'status', 'assigned_technician', 'scheduled_date', 'notes']
        widgets = {
            'ticket': forms.Select(attrs={'class': 'form-control custom-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição dos serviços a serem realizados'}),
            'status': forms.Select(attrs={'class': 'form-control custom-select'}),
            'assigned_technician': forms.Select(attrs={'class': 'form-control custom-select'}),
            # CORREÇÃO: Adicionado 'format' para corresponder ao padrão HTML5 para datetime-local
            'scheduled_date': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control', 'type': 'datetime-local'}),
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
        self.fields['ticket'].queryset = Ticket.objects.exclude(status__in=['FECHADO', 'RESOLVIDO'])


class TicketCommentForm(forms.ModelForm):
    # CORREÇÃO: Usar o novo MultipleFileField em vez do FileField padrão
    attachments = MultipleFileField(
        required=False,
        label="Anexar ficheiros"
    )

    class Meta:
        model = TicketComment
        fields = ['comment', 'is_internal_note']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adicione um comentário ou uma nota interna...'}),
            'is_internal_note': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'comment': '', # O placeholder já é suficiente
            'is_internal_note': 'Marcar como nota interna (visível apenas para a equipa)',
        }
