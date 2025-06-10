# ticket_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

# Assumindo que a sua estrutura de projeto é 'apps.nome_do_app'
# Se não for, remova o prefixo 'apps.' (ex: 'dashboard.urls')

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Dashboard agora está explicitamente em /dashboard/
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),

    path('servicedesk/', include('apps.servicedesk.urls', namespace='servicedesk')),
    path('customers/', include('apps.customers.urls', namespace='customers')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('inventory/', include('apps.inventory.urls', namespace='inventory')),
    path('quotes/', include('apps.quotes.urls', namespace='quotes')),

    # URLs de Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # 2. A URL raiz ('/') agora redireciona para o dashboard
    path('', RedirectView.as_view(url='/dashboard/', permanent=True), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

