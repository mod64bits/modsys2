from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Ticket, Atendimento, MensagemAtendimento
from .serializers import TicketSerializer, AtendimentoSerializer, MensagemAtendimentoSerializer

# Create your views here.

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['id', 'cliente__nome', 'solicitante', 'departamento']

class AtendimentoViewSet(viewsets.ModelViewSet):
    queryset = Atendimento.objects.all()
    serializer_class = AtendimentoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['protocolo', 'ticket__id', 'ticket__cliente__nome']

class MensagemAtendimentoViewSet(viewsets.ModelViewSet):
    queryset = MensagemAtendimento.objects.all()
    serializer_class = MensagemAtendimentoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['mensagem', 'atendimento__protocolo', 'cliente__nome']
