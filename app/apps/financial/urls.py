# financial/urls.py
from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    path('contas-a-receber/', views.contareceber_list, name='contareceber_list'),
    path('contas-a-receber/<int:pk>/', views.contareceber_detail, name='contareceber_detail'),
    path('contas-a-receber/<int:pk>/add-payment/', views.add_payment_modal, name='add_payment_modal'),

    # Nova URL para gerar o PDF do recibo
    path('contas-a-receber/<int:pk>/receipt-pdf/', views.contareceber_receipt_pdf_view, name='contareceber_receipt_pdf'),

    path('orcamento/<int:orcamento_pk>/gerar-fatura/', views.generate_conta_from_orcamento, name='generate_conta_from_orcamento'),
]