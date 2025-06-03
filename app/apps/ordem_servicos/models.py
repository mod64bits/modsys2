from django.db import models
from django.contrib.auth.models import User
from apps.clientes.models import Cliente, Equipe
from django.utils import timezone
import datetime
from apps.base.models import BaseModel
import os
from django.conf import settings

def upload_to_atendimentos(instance, filename):
    # Cria um caminho baseado no protocolo do atendimento
    protocolo = instance.atendimento.protocolo
    return os.path.join('atendimentos', protocolo, filename)

class Ticket(BaseModel):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_andamento', 'Em Andamento'),
        ('fechado', 'Fechado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='tickets')
    solicitante = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='tickets')
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')

    def __str__(self):
        return f"Ticket {self.id} - {self.status}"



    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-created']

class Atendimento(BaseModel):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='atendimento')
    protocolo = models.CharField(max_length=20, unique=True, editable=False)
    descricao = models.TextField()
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.protocolo:
            self.protocolo = self.generate_protocolo()
        super().save(*args, **kwargs)

    def generate_protocolo(self):
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        last_atendimento = Atendimento.objects.filter(protocolo__startswith=date_str).order_by('-protocolo').first()
        
        if last_atendimento:
            last_number = int(last_atendimento.protocolo[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
            
        return f"{date_str}{new_number:04d}"

    def __str__(self):
        return f"Atendimento {self.protocolo} - {self.ticket.status}"

    class Meta:
        verbose_name = "Atendimento"
        verbose_name_plural = "Atendimentos"
        ordering = ['-created']

class MensagemAtendimento(BaseModel):
    atendimento = models.ForeignKey(Atendimento, on_delete=models.CASCADE, related_name='mensagens')
    mensagem = models.TextField()
    atendente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    arquivo = models.FileField(upload_to=upload_to_atendimentos, null=True, blank=True)


    def __str__(self):
        return f"Mensagem de {self.atendente.email if self.atendente else 'Sistema'} - {self.created}"

    class Meta:
        verbose_name = "Mensagem de Atendimento"
        verbose_name_plural = "Mensagens de Atendimento"
        ordering = ['-created']
