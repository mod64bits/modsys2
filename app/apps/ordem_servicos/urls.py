from django.urls import path
from . import views

app_name = 'ordens'
urlpatterns = [
    path('', views.HomeOrdemDeServicosView.as_view(), name='ticket_home'),
    path('novo/', views.HomeOrdemDeServicosView.as_view(), name='ticket_novo'),
]