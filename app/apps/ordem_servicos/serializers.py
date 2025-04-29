from rest_framework import serializers
from .models import Ticket, Atendimento, MensagemAtendimento
from clientes.serializers import ClienteSerializer
from clientes.models import Cliente
class MensagemAtendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensagemAtendimento
        fields = [
            'id', 'atendimento', 'mensagem', 'cliente',
            'atendente', 'arquivo', 'data_criacao'
        ]
        read_only_fields = ['data_criacao']

class AtendimentoSerializer(serializers.ModelSerializer):
    mensagens = MensagemAtendimentoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Atendimento
        fields = [
            'id', 'protocolo', 'ticket', 'descricao',
            'data_atendimento', 'responsavel', 'mensagens'
        ]
        read_only_fields = ['protocolo', 'data_atendimento']

class TicketSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        source='cliente',
        write_only=True
    )
    atendimento = AtendimentoSerializer(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'cliente', 'cliente_id', 'solicitante', 
            'departamento', 'descricao', 'responsavel',
            'iniciado_em', 'status', 'fechado_em', 'atendimento'
        ]
        read_only_fields = ['iniciado_em', 'fechado_em'] 