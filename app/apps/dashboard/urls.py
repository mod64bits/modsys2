# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard_page'),
    path('api/data/', views.dashboard_data_api, name='data_api'),
    path('update-status/<str:model_name>/<int:pk>/', views.update_status_modal, name='update_status'),
]
