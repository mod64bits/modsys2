from .models import Cliente
from bootstrap_modal_forms.forms import BSModalModelForm


class ClienteForm(BSModalModelForm):
    class Meta:
        model = Cliente
        fields = "__all__"
