from django.contrib.auth.mixins import LoginRequiredMixin
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalReadView, BSModalDeleteView
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from .forms import ClienteForm
from .models import Cliente


class ListaClientesView(ListView):
    model = Cliente
    template_name = 'clientes/lista_clientes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_open_cadastro'] = True
        context['active_clientes'] = True
        return context


class NovoClienteView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'clientes/novo_cliente.html'
    form_class = ClienteForm
    success_message = 'Success: Cliente was created.'
    success_url = reverse_lazy('clientes:lista_cliente')


class EditarClienteView(LoginRequiredMixin, BSModalUpdateView):
    model = Cliente
    template_name = 'clientes/editar_cliente.html'
    form_class = ClienteForm
    success_message = 'Success: Cliente was updated.'
    success_url = reverse_lazy('clientes:lista_cliente')


class DeletarClienteView(LoginRequiredMixin, BSModalDeleteView):
    model = Cliente
    template_name = 'clientes/delete_cliente.html'
    success_message = 'Success: Cliente was deleted.'
    success_url = reverse_lazy('clientes:lista_cliente')



