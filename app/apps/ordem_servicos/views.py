from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView
from apps.ordem_servicos.models import Ticket, MensagemAtendimento, Atendimento
from .forms import AbrirTicketForm
from ..clientes.models import Cliente
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeOrdemDeServicosView(TemplateView):
    template_name = "ordem_servicos/home.html"

class NovoTicketView(BSModalCreateView):
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



class TicketDetailView(DetailView):
    model = Ticket
    template_name = 'ordem_servicos/ticket_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_ordem'] = True
        context['active_tickt_list'] = True
        return context

    def atendimento(self):
        atendimento = Atendimento.objects.get(ticket=self.object)
        return atendimento

class MensagemAtendimentoListView(LoginRequiredMixin, ListView):
    model = MensagemAtendimento
    template_name = 'ordem_servicos/mensagem_atendimento_list.html'
    context_object_name = 'mensagens'

    def get_queryset(self):
        atendimento_id = self.kwargs.get('atendimento_id')
        return MensagemAtendimento.objects.filter(atendimento_id=atendimento_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['atendimento'] = Atendimento.objects.get(id=self.kwargs.get('atendimento_id'))
        return context

class MensagemAtendimentoCreateView(LoginRequiredMixin, CreateView):
    model = MensagemAtendimento
    template_name = 'ordem_servicos/mensagem_atendimento_form.html'
    fields = ['mensagem', 'arquivo']
    success_url = reverse_lazy('mensagem-atendimento-list')

    def form_valid(self, form):
        form.instance.atendimento_id = self.kwargs.get('atendimento_id')
        form.instance.atendente = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mensagem-atendimento-list', kwargs={'atendimento_id': self.kwargs.get('atendimento_id')})


class AddAtendimentoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        ticket_id = kwargs.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)
        atendimento = Atendimento.objects.create(ticket=ticket, atendente=request.user)
        return redirect(reverse_lazy('ordens:ticket_detail', kwargs={'pk': ticket_id}))