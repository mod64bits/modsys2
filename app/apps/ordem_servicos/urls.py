from django.urls import path
from . import views
from .views import MensagemAtendimentoListView, MensagemAtendimentoCreateView

app_name = 'ordens'
urlpatterns = [
    path('', views.HomeOrdemDeServicosView.as_view(), name='ticket_home'),
    path('tikets/', views.TicketListView.as_view(), name='ticket_lista'),
    path('tickets/novo/<uuid:cliente_id>/', views.NovoTicketView.as_view(), name='ticket_create'),
    path('tickets/<uuid:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('atendimento/<int:atendimento_id>/mensagens/', 
         MensagemAtendimentoListView.as_view(), 
         name='mensagem-atendimento-list'),
    path('atendimento/<int:atendimento_id>/mensagens/nova/', 
         MensagemAtendimentoCreateView.as_view(), 
         name='mensagem-atendimento-create'),
]