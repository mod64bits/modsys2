from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, AtendimentoViewSet, MensagemAtendimentoViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'atendimentos', AtendimentoViewSet)
router.register(r'mensagens', MensagemAtendimentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 