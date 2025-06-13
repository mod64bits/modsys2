# servicedesk/urls.py
from django.urls import path
from . import views

app_name = 'servicedesk'

urlpatterns = [
    # URLs para Tickets
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/new/modal/', views.ticket_create_modal, name='ticket_create_modal'),
    path('tickets/<int:pk>/edit/modal/', views.ticket_update_modal, name='ticket_update_modal'),
    path('tickets/<int:pk>/detail/modal/', views.ticket_detail_modal, name='ticket_detail_modal'),
    path('tickets/<int:pk>/delete/modal/', views.ticket_delete_modal, name='ticket_delete_modal'),
    path('tickets/<int:pk>/pdf/', views.ticket_pdf_view, name='ticket_pdf'),
    path('tickets/<int:pk>/add_comment/', views.add_ticket_comment, name='add_ticket_comment'),

    # URLs para Ordens de Serviço (Work Orders)
    path('workorders/', views.work_order_list, name='work_order_list'),
    # A URL 'create' pode ser um modal ou uma página completa, dependendo da sua preferência
    path('workorders/new/', views.work_order_create_view, name='work_order_create'), # Exemplo de rota para página completa de criação
    # A URL de edição aponta para a view de página completa para gerir produtos
    path('workorders/<int:pk>/edit/', views.work_order_update_view, name='work_order_update'),
    path('workorders/<int:pk>/detail/modal/', views.work_order_detail_modal, name='work_order_detail_modal'),
    path('workorders/<int:pk>/delete/modal/', views.work_order_delete_modal, name='work_order_delete_modal'),
    path('workorders/<int:pk>/pdf/', views.work_order_pdf_view, name='work_order_pdf'),
]
