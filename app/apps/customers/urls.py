# customers/urls.py
from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('new/modal/', views.customer_create_modal, name='customer_create_modal'),
    path('<int:pk>/detail/modal/', views.customer_detail_modal, name='customer_detail_modal'),
    path('<int:pk>/edit/modal/', views.customer_update_modal, name='customer_update_modal'),
    path('<int:pk>/delete/modal/', views.customer_delete_modal, name='customer_delete_modal'),
]
