# reports/forms.py
from django import forms
from apps.customers.models import Customer
from django.utils import timezone

class ReportFilterForm(forms.Form):
    CONTENT_CHOICES = [
        ('all', 'Tickets e Ordens de Serviço'),
        ('tickets_only', 'Somente Tickets'),
        ('work_orders_only', 'Somente Ordens de Serviço'),
    ]

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        label="Cliente",
        widget=forms.Select(attrs={'class': 'form-control custom-select select2-filter'})
    )
    start_date = forms.DateField(
        required=False,
        label="Data Inicial",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        # initial=timezone.now().replace(day=1) # Exemplo: primeiro dia do mês atual
    )
    end_date = forms.DateField(
        required=False,
        label="Data Final",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        # initial=timezone.now() # Exemplo: data atual
    )
    content_type = forms.ChoiceField(
        choices=CONTENT_CHOICES,
        required=True,
        label="Tipo de Conteúdo",
        initial='all',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', "A data final não pode ser anterior à data inicial.")

        # Adicionar um dia ao end_date para incluir todo o dia na consulta <= end_date
        # if end_date:
        #     cleaned_data['end_date'] = end_date + timezone.timedelta(days=1)

        return cleaned_data
