# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [

    path('mark-as-read/', views.mark_as_read, name='mark_as_read'),
    # Pode adicionar uma URL para a página "Ver Todas" no futuro
    # path('all/', views.all_notifications_view, name='all_notifications'),
]