# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard_page'),
    path('financial/', views.financial_dashboard_view, name='financial_dashboard_page'),

    # Rota ÚNICA para obter todos os dados do dashboard via AJAX
    path('api/data/', views.dashboard_data_api, name='data_api'),

    path('update-status/<str:model_name>/<int:pk>/', views.update_status_modal, name='update_status'),
]
