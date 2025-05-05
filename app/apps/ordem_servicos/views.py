from django.views.generic import TemplateView, CreateView
from django.views.generic.list import ListView
from apps.ordem_servicos.models import Ticket


class HomeOrdemDeServicosView(TemplateView):
    template_name = "ordem_servicos/home.html"

class TicketOrdemDeServicosView(CreateView):
    model = Ticket
    template_name = "ordem_servicos/nova_ordem.html"
    fields = "__all__"

class TicketListView(ListView):
    model = Ticket
    template_name = 'ordem_servicos/ticket_list.html'

