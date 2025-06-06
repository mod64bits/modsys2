from django import forms

from .models import Ticket
import django_filters
from bootstrap_modal_forms.forms import BSModalModelForm
from apps.clientes.models import Cliente, Equipe


class AbrirTicketForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        # Pegamos o cliente para filtrar os membros da equipe
        cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)

        if cliente:
            # Filtramos os membros da equipe associados ao cliente
            self.fields['solicitante'].queryset = Equipe.objects.filter(clientes=cliente)
        else:
            # Por padrão, nenhum membro da equipe estará disponível
            self.fields['solicitante'].queryset = Equipe.objects.none()

    class Meta:
        model = Ticket
        fields = ['cliente', 'solicitante', 'descricao']
        widgets = {
            'cliente': forms.HiddenInput(),
            'solicitante': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }




# class ProductFilter(django_filters.FilterSet):
#     name = django_filters.CharFilter(lookup_expr='iexact')
#
#     class Meta:
#         model = Ticket
#         fields = ['status', 'cliente', 'responsavel', 'created_at']