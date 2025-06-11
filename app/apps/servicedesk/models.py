# servicedesk/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

def ticket_attachment_path(instance, filename):
    return f'tickets/{instance.comment.ticket.id}/{filename}'

class Category(models.Model):
    """Modelo para categorizar tickets (ex: Hardware, Software, Rede)."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']


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

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoria",
        related_name='tickets'
    )

    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cliente",
        related_name='tickets'
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


class TicketComment(models.Model):
    class CommentType(models.TextChoices):
        COMMENT = 'COMMENT', _('Comentário')
        LOG = 'LOG', _('Registo de Atividade')

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments', verbose_name=_("Ticket"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Autor"), help_text=_("Se nulo, é um registo do sistema."))
    comment = models.TextField(verbose_name=_("Comentário / Atividade"))
    comment_type = models.CharField(max_length=10, choices=CommentType.choices, default=CommentType.COMMENT, verbose_name=_("Tipo"))
    is_internal_note = models.BooleanField(default=False, verbose_name=_("É uma nota interna?"), help_text=_("Notas internas são visíveis apenas para a equipa."))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        author_name = self.author.get_full_name() if self.author and self.author.get_full_name() else (self.author.username if self.author else "Sistema")
        return f'Comentário de {author_name} no ticket #{self.ticket.id}'

    class Meta:
        verbose_name = "Comentário de Ticket"
        verbose_name_plural = "Comentários de Tickets"
        ordering = ['created_at']


class Attachment(models.Model):
    comment = models.ForeignKey(TicketComment, on_delete=models.CASCADE, related_name='attachments', verbose_name=_("Comentário Associado"))
    file = models.FileField(upload_to=ticket_attachment_path, verbose_name=_("Ficheiro"))
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_("Enviado por"))

    def __str__(self):
        return self.file.name.split('/')[-1]

    @property
    def filename(self):
        return self.file.name.split('/')[-1]

    @property
    def filesize(self):
        try:
            return f"{self.file.size / 1024:.2f} KB"
        except (OSError, FileNotFoundError):
            return "0 KB"


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

    assigned_technician = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_work_orders', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Técnico Responsável")

    scheduled_date = models.DateTimeField(null=True, blank=True, verbose_name="Data Agendada")
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão")

    notes = models.TextField(blank=True, null=True, verbose_name="Observações Internas")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação da OS")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização da OS")

    def __str__(self):
        return f"OS #{self.id} para Ticket #{self.ticket.id}"

    @property
    def customer(self):
        return self.ticket.customer

    class Meta:
        verbose_name = "Ordem de Serviço"
        verbose_name_plural = "Ordens de Serviço"
        ordering = ['-created_at']

@receiver(post_save, sender=Ticket)
def ticket_post_save_receiver(sender, instance, created, **kwargs):
    """
    Quando um Ticket é guardado, verifica se o seu estado é 'FECHADO' ou 'RESOLVIDO'.
    Se for, todas as WorkOrders abertas relacionadas são atualizadas para 'CONCLUIDA'.
    """
    ticket = instance

    if hasattr(ticket, '_skip_signal_handler') and ticket._skip_signal_handler:
        return

    if ticket.status in ['FECHADO', 'RESOLVIDO']:
        work_orders_to_update = ticket.work_orders.exclude(status__in=['CONCLUIDA', 'CANCELADA'])
        for wo in work_orders_to_update:
            wo.status = 'CONCLUIDA'
            if not wo.completion_date:
                wo.completion_date = timezone.now()

            wo._skip_signal_handler = True
            wo.save(update_fields=['status', 'completion_date'])
            delattr(wo, '_skip_signal_handler')


@receiver(post_save, sender=WorkOrder)
def work_order_post_save_receiver(sender, instance, created, **kwargs):
    """
    Quando uma WorkOrder é guardada, verifica se o seu estado é 'CONCLUIDA' ou 'CANCELADA'.
    Se for, verifica se todas as outras WorkOrders do mesmo Ticket também estão nesses estados.
    Se todas estiverem, o Ticket pai é atualizado para 'RESOLVIDO'.
    """
    work_order = instance
    ticket = work_order.ticket

    if hasattr(work_order, '_skip_signal_handler') and work_order._skip_signal_handler:
        return

    if work_order.status in ['CONCLUIDA', 'CANCELADA'] and ticket.status not in ['RESOLVIDO', 'FECHADO']:
        all_work_orders = ticket.work_orders.all()

        if all_work_orders.exists():
            all_closed_or_cancelled = not all_work_orders.exclude(status__in=['CONCLUIDA', 'CANCELADA']).exists()
        else:
            all_closed_or_cancelled = True

        if all_closed_or_cancelled:
            ticket._skip_signal_handler = True
            ticket.status = 'RESOLVIDO'
            ticket.save(update_fields=['status'])
            delattr(ticket, '_skip_signal_handler')
