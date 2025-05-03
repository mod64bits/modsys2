from django.views.generic import TemplateView, CreateView

from apps.ordem_servicos.models import Ticket


class HomeOrdemDeServicosView(TemplateView):
    template_name = "ordem_servicos/home.html"

class TicketOrdemDeServicosView(CreateView):
    model = Ticket
    template_name = "ordem_servicos/nova_ordem.html"
    fields = "__all__"
