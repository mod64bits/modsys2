from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, CreateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView
from apps.ordem_servicos.models import Ticket
from .forms import AbrirTicketForm
from ..clientes.models import Cliente


class HomeOrdemDeServicosView(TemplateView):
    template_name = "ordem_servicos/home.html"

class NovoTicketView(CreateView):
    template_name = "ordem_servicos/novo_ticket.html"
    form_class = AbrirTicketForm
    success_message = 'Success: Ticket aberto com sucesso!'
    success_url = reverse_lazy('ordens:ticket_lista')

    def get_form_kwargs(self):
        """
        Adiciona o cliente ao contexto do formulário.
        """
        kwargs = super().get_form_kwargs()
        cliente_id = self.kwargs.get('cliente_id')
        cliente = get_object_or_404(Cliente, id=cliente_id)  # Obtém o cliente pelo ID
        kwargs['cliente'] = cliente  # Passa o cliente para o formulário
        return kwargs

    def get_initial(self):
        """
        Preenche o cliente automaticamente no formulário (se necessário).
        """
        initial = super().get_initial()
        cliente_id = self.kwargs.get('cliente_id')
        initial['cliente'] = get_object_or_404(Cliente, id=cliente_id)
        return initial

class TicketListView(ListView):
    model = Ticket
    template_name = 'ordem_servicos/ticket_list.html'

    def get_queryset(self, *args, **kwargs):
        qs = super(TicketListView, self).get_queryset(*args, **kwargs)
        qs = qs.filter(status='aberto').order_by('-created')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_ordem'] = True
        context['active_tickt_list'] = True
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clientes'] = Cliente.objects.all()
        return context

