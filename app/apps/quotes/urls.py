# quotes/urls.py
from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    path('', views.orcamento_list, name='orcamento_list'),
    path('new/', views.orcamento_create_view, name='orcamento_create'),
    path('<int:pk>/', views.orcamento_detail_view, name='orcamento_detail'),
    path('<int:pk>/update/', views.orcamento_update_view, name='orcamento_update'),
    path('<int:pk>/delete/', views.orcamento_delete_view, name='orcamento_delete'),
    path('<int:pk>/pdf/', views.orcamento_pdf_view, name='orcamento_pdf'),

    # URL para AJAX de detalhes do produto (usado no formulário de orçamento)
    path('ajax/get-product-details/<int:product_id>/', views.get_product_details_json, name='ajax_get_product_details'),
    path('<int:pk>/generate-os/', views.generate_os_from_quote, name='generate_os_from_quote'),
]
