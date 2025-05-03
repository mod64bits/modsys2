from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeOrdemDeServicosView.as_view(), name='ordens_home'),
    path('novo/', views.HomeOrdemDeServicosView.as_view(), name='ordens_novo'),
]