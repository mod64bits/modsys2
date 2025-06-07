# inventory/urls.py
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # URLs para Fornecedor
    path('suppliers/', views.fornecedor_list, name='fornecedor_list'),
    path('suppliers/new/modal/', views.fornecedor_create_modal, name='fornecedor_create_modal'),
    path('suppliers/<int:pk>/detail/modal/', views.fornecedor_detail_modal, name='fornecedor_detail_modal'),
    path('suppliers/<int:pk>/edit/modal/', views.fornecedor_update_modal, name='fornecedor_update_modal'),
    path('suppliers/<int:pk>/delete/modal/', views.fornecedor_delete_modal, name='fornecedor_delete_modal'),

    # URLs para Categoria de Produto
    path('categories/', views.categoriaproduto_list, name='categoriaproduto_list'),
    path('categories/new/modal/', views.categoriaproduto_create_modal, name='categoriaproduto_create_modal'),
    path('categories/<int:pk>/detail/modal/', views.categoriaproduto_detail_modal, name='categoriaproduto_detail_modal'),
    path('categories/<int:pk>/edit/modal/', views.categoriaproduto_update_modal, name='categoriaproduto_update_modal'),
    path('categories/<int:pk>/delete/modal/', views.categoriaproduto_delete_modal, name='categoriaproduto_delete_modal'),

    # URLs para Produto
    path('products/', views.produto_list, name='produto_list'),
    path('products/new/modal/', views.produto_create_modal, name='produto_create_modal'),
    path('products/<int:pk>/detail/modal/', views.produto_detail_modal, name='produto_detail_modal'),
    path('products/<int:pk>/edit/modal/', views.produto_update_modal, name='produto_update_modal'),
    path('products/<int:pk>/delete/modal/', views.produto_delete_modal, name='produto_delete_modal'),
]
