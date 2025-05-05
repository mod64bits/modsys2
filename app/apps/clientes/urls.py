from django.urls import path

from .views import ListaClientesView, NovoClienteView, EditarClienteView, DeletarClienteView


app_name = 'clientes'

urlpatterns = [
    path('', ListaClientesView.as_view(), name='lista_cliente'),
    path('novo/', NovoClienteView.as_view(), name='novo_cliente'),
    path('editar/<uuid:pk>/', EditarClienteView.as_view(), name='editar_cliente'),
    path('deletar/<uuid:pk>/', DeletarClienteView.as_view(), name='deletar_cliente'),

]
