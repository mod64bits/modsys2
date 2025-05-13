from django.urls import path
from . import views

app_name = 'ordens'
urlpatterns = [
    path('', views.HomeOrdemDeServicosView.as_view(), name='ticket_home'),
    path('tikets/', views.TicketListView.as_view(), name='ticket_lista'),
    path('tickets/novo/<uuid:cliente_id>/', views.NovoTicketView.as_view(), name='ticket_create'),
]