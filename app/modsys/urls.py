"""
URL configuration for modsys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
     path('servicedesk/', include('apps.servicedesk.urls', namespace='servicedesk')),
    path('customers/', include('apps.customers.urls', namespace='customers')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('inventory/', include('apps.inventory.urls', namespace='inventory')),
    path('quotes/', include('apps.quotes.urls', namespace='quotes')),
    # URLs de Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Redireciona a URL raiz '/' para a lista de tickets
    path('', RedirectView.as_view(url='/servicedesk/tickets/', permanent=True)),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )