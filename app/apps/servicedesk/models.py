# servicedesk/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('AGUARDANDO_CLIENTE', 'Aguardando Cliente'),
        ('RESOLVIDO', 'Resolvido'),
        ('FECHADO', 'Fechado'),
    ]

    PRIORITY_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição Detalhada")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO', verbose_name="Status")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIA', verbose_name="Prioridade")

    # Novo campo para relacionar com o cliente
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cliente",
        related_name='tickets' # Nome do relacionamento reverso a partir do Cliente
    )

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tickets', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Criado Por")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_tickets', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Atribuído Para")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def __str__(self):
        return f"#{self.id} - {self.title}"

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-created_at']

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('AGENDADA', 'Agendada'),
        ('EM_EXECUCAO', 'Em Execução'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='work_orders', verbose_name="Ticket Relacionado")
    description = models.TextField(verbose_name="Descrição dos Serviços")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status da OS")

    # Novo campo para relacionar com o cliente (pode ser redundante se o Ticket já tem, mas útil para acesso direto)
    # Se a WorkOrder SEMPRE pertence ao mesmo cliente do Ticket, este campo pode ser omitido e acessado via work_order.ticket.customer
    # No entanto, para consistência e acesso direto, pode ser mantido.
    # Se optar por manter, considere uma lógica para garantir que seja o mesmo cliente do ticket.
    # Por simplicidade, vou assumir que a OS pertence ao mesmo cliente do Ticket e omitir aqui,
    # acessando via work_order.ticket.customer. Se precisar de um cliente diferente para a OS, adicione o campo abaixo.
    # customer = models.ForeignKey(
    #     'customers.Customer',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name="Cliente da OS",
    #     related_name='direct_work_orders'
    # )

    assigned_technician = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_work_orders', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Técnico Responsável")

    scheduled_date = models.DateTimeField(null=True, blank=True, verbose_name="Data Agendada")
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão")

    notes = models.TextField(blank=True, null=True, verbose_name="Observações Internas")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação da OS")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização da OS")

    def __str__(self):
        return f"OS #{self.id} para Ticket #{self.ticket.id}"

    # Propriedade para acessar facilmente o cliente do ticket associado
    @property
    def customer(self):
        return self.ticket.customer

    class Meta:
        verbose_name = "Ordem de Serviço"
        verbose_name_plural = "Ordens de Serviço"
        ordering = ['-created_at']

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Comentário de {self.author} em {self.ticket.title}"

# Signals para lógica de cascata de status

@receiver(post_save, sender=Ticket)
def ticket_post_save_receiver(sender, instance, created, **kwargs):
    """
    Quando um Ticket é salvo, verifica se seu status é 'FECHADO' ou 'RESOLVIDO'.
    Se for, todas as WorkOrders abertas relacionadas são atualizadas para 'CONCLUIDA'.
    """
    ticket = instance
    if hasattr(ticket, '_skip_signal_handler') and ticket._skip_signal_handler:
        return

    if ticket.status in ['FECHADO', 'RESOLVIDO']:
        work_orders_to_update = ticket.work_orders.exclude(status__in=['CONCLUIDA', 'CANCELADA'])
        for wo in work_orders_to_update:
            wo.status = 'CONCLUIDA'
            if wo.status == 'CONCLUIDA' and not wo.completion_date:
                wo.completion_date = timezone.now()

            wo._skip_signal_handler = True
            wo.save(update_fields=['status', 'completion_date'])
            delattr(wo, '_skip_signal_handler')


@receiver(post_save, sender=WorkOrder)
def work_order_post_save_receiver(sender, instance, created, **kwargs):
    """
    Quando uma WorkOrder é salva, verifica se seu status é 'CONCLUIDA' ou 'CANCELADA'.
    Se for, verifica se todas as outras WorkOrders do mesmo Ticket também estão nesses status.
    Se todas estiverem, o Ticket pai é atualizado para 'RESOLVIDO'.
    """
    work_order = instance
    ticket = work_order.ticket

    if hasattr(work_order, '_skip_signal_handler') and work_order._skip_signal_handler:
        return

    if work_order.status in ['CONCLUIDA', 'CANCELADA'] and ticket.status not in ['RESOLVIDO', 'FECHADO']:
        all_work_orders = ticket.work_orders.all()
        all_closed_or_cancelled = True
        if not all_work_orders.exists():
            all_closed_or_cancelled = True
        else:
            for wo_item in all_work_orders: # Renomeado para evitar conflito com wo no loop externo do outro signal
                if wo_item.status not in ['CONCLUIDA', 'CANCELADA']:
                    all_closed_or_cancelled = False
                    break

        if all_closed_or_cancelled:
            ticket._skip_signal_handler = True
            ticket.status = 'RESOLVIDO'
            ticket.save(update_fields=['status'])
            delattr(ticket, '_skip_signal_handler')

