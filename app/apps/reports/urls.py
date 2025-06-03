# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_filter_view, name='report_filter_page'),
    path('pdf/', views.generate_filtered_pdf_view, name='generate_filtered_pdf'),
]
