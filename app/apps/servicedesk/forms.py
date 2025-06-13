# servicedesk/forms.py
from django import forms
from django.forms import inlineformset_factory, NumberInput
from .models import Ticket, WorkOrder, TicketComment, Category, ProdutoUtilizadoOS
from apps.inventory.models import Produto
from apps.customers.models import Customer

class MultipleFileInput(forms.ClearableFileInput): allow_multiple_selected = True
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True})); super().__init__(*args, **kwargs)
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)): return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)

class TicketForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=Customer.objects.order_by('nome'), required=False, widget=forms.Select(attrs={'class': 'form-control custom-select'}), label="Cliente")
    category = forms.ModelChoiceField(queryset=Category.objects.order_by('name'), required=False, widget=forms.Select(attrs={'class': 'form-control custom-select'}), label="Categoria")
    class Meta:
        model = Ticket
        fields = ['title', 'customer', 'category', 'description', 'priority', 'status', 'assigned_to']
        widgets = { 'title': forms.TextInput(attrs={'class': 'form-control'}), 'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}), 'priority': forms.Select(attrs={'class': 'form-control custom-select'}), 'status': forms.Select(attrs={'class': 'form-control custom-select'}), 'assigned_to': forms.Select(attrs={'class': 'form-control custom-select'}), }

class ProdutoUtilizadoOSForm(forms.ModelForm):
    produto_lookup = forms.ModelChoiceField(queryset=Produto.objects.filter(ativo=True).order_by('nome'), label="Buscar Produto", required=True, widget=forms.Select(attrs={'class': 'form-control custom-select select2-field product-lookup'}))
    class Meta:
        model = ProdutoUtilizadoOS
        fields = ['produto', 'quantidade', 'preco_compra_no_momento', 'preco_venda_no_momento']
        widgets = { 'produto': forms.HiddenInput(), 'quantidade': NumberInput(attrs={'class': 'form-control item-calc'}), 'preco_compra_no_momento': NumberInput(attrs={'class': 'form-control readonly-field', 'readonly': 'readonly'}), 'preco_venda_no_momento': NumberInput(attrs={'class': 'form-control item-calc'}), }

ProdutoUtilizadoOSFormSet = inlineformset_factory(WorkOrder, ProdutoUtilizadoOS, form=ProdutoUtilizadoOSForm, extra=1, can_delete=True)

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['ticket', 'description', 'status', 'assigned_technician', 'scheduled_date', 'notes']
        widgets = { 'ticket': forms.Select(attrs={'class': 'form-control custom-select'}), 'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), 'status': forms.Select(attrs={'class': 'form-control custom-select'}), 'assigned_technician': forms.Select(attrs={'class': 'form-control custom-select'}), 'scheduled_date': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control', 'type': 'datetime-local'}), 'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ticket'].queryset = Ticket.objects.exclude(status__in=['FECHADO', 'RESOLVIDO'])

class TicketCommentForm(forms.ModelForm):
    attachments = MultipleFileField(required=False, label="Anexar ficheiros")
    class Meta:
        model = TicketComment
        fields = ['comment', 'is_internal_note']
        widgets = { 'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), 'is_internal_note': forms.CheckboxInput(attrs={'class': 'form-check-input'}), }
        labels = { 'comment': '', 'is_internal_note': 'Marcar como nota interna', }
