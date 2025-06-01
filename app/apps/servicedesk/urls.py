# servicedesk/urls.py
from django.urls import path
from . import views

app_name = 'servicedesk'

urlpatterns = [
    path('tickets/', views.ticket_list, name='ticket_list'),

    # URLs para carregar conteúdo de modais de Ticket (AJAX)
    path('tickets/new/modal/', views.ticket_create_modal, name='ticket_create_modal'),
    path('tickets/<int:pk>/edit/modal/', views.ticket_update_modal, name='ticket_update_modal'),
    path('tickets/<int:pk>/detail/modal/', views.ticket_detail_modal, name='ticket_detail_modal'),
    path('tickets/<int:pk>/delete/modal/', views.ticket_delete_modal, name='ticket_delete_modal'),

    # URLs para WorkOrders
    path('workorders/', views.work_order_list, name='work_order_list'),
    path('workorders/new/modal/', views.work_order_create_modal, name='work_order_create_modal'),
    path('workorders/<int:pk>/edit/modal/', views.work_order_update_modal, name='work_order_update_modal'),
    path('workorders/<int:pk>/detail/modal/', views.work_order_detail_modal, name='work_order_detail_modal'),
    path('workorders/<int:pk>/delete/modal/', views.work_order_delete_modal, name='work_order_delete_modal'),

    # Você pode adicionar URLs para visualização completa (não modal) se necessário
    # path('tickets/new/', views.ticket_create_full, name='ticket_create_full'),
    # path('tickets/<int:pk>/', views.ticket_detail_full, name='ticket_detail_full'),
    # path('workorders/new/', views.work_order_create_full, name='work_order_create_full'),
    # path('workorders/<int:pk>/', views.work_order_detail_full, name='work_order_detail_full'),
]
