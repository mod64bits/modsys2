from .models import Ticket
import django_filters
from bootstrap_modal_forms.forms import BSModalModelForm

class AbrirTicketForm(BSModalModelForm):
    class Meta:
        model = Ticket
        exclude = ['status']


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Ticket
        fields = ['status', 'cliente', 'responsavel', 'created_at']