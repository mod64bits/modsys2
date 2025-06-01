# servicedesk/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

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

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tickets', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Criado Por")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_tickets', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Atribuído Para")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    # Campos adicionais que podem ser úteis:
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    resolution_details = models.TextField(blank=True, null=True, verbose_name="Detalhes da Resolução")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de Fechamento")

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

    assigned_technician = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_work_orders', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Técnico Responsável")

    scheduled_date = models.DateTimeField(null=True, blank=True, verbose_name="Data Agendada")
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão")

    notes = models.TextField(blank=True, null=True, verbose_name="Observações Internas")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação da OS")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização da OS")

    def __str__(self):
        return f"OS #{self.id} para Ticket #{self.ticket.id}"

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

@receiver(post_save, sender=WorkOrder)
def work_order_post_save_receiver(sender, instance, created, **kwargs):
    """
    Quando uma WorkOrder é salva, verifica se seu status é 'CONCLUIDA' ou 'CANCELADA'.
    Se for, verifica se todas as outras WorkOrders do mesmo Ticket também estão nesses status.
    Se todas estiverem, o Ticket pai é atualizado para 'RESOLVIDO'.
    """
    work_order = instance
    ticket = work_order.ticket

    # Evita recursão se a atualização da work_order for desencadeada por uma atualização de Ticket
    if hasattr(work_order, '_skip_signal_handler') and work_order._skip_signal_handler:
        return

    # Verifica apenas se o status da WorkOrder mudou para um estado final
    # e se o ticket ainda não está em um estado final.
    if work_order.status in ['CONCLUIDA', 'CANCELADA'] and ticket.status not in ['RESOLVIDO', 'FECHADO']:
        # Verifica o status de todas as WorkOrders associadas ao Ticket
        all_work_orders = ticket.work_orders.all()
        all_closed_or_cancelled = True
        if not all_work_orders.exists(): # Se não há OS, o ticket pode ser considerado resolvido (depende da regra)
            all_closed_or_cancelled = True # Ou False, dependendo da regra de negócio
        else:
            for wo in all_work_orders:
                if wo.status not in ['CONCLUIDA', 'CANCELADA']:
                    all_closed_or_cancelled = False
                    break

        if all_closed_or_cancelled:
            # Antes de salvar o ticket, defina um atributo para pular o signal handler do Ticket
            ticket._skip_signal_handler = True
            ticket.status = 'RESOLVIDO' # Ou 'FECHADO', dependendo da lógica de negócio
            ticket.save(update_fields=['status'])
            delattr(ticket, '_skip_signal_handler') # Remove o atributo após salvar


# É importante registrar os signals. Em apps Django mais recentes,
# a configuração em apps.py com AppConfig.ready() é a forma preferida.
# No entanto, para este exemplo, a simples importação dos signals no models.py
# ou em __init__.py do app geralmente funciona se o models.py for carregado.
# Para garantir o carregamento, você pode importar os signals no método ready()
# do arquivo servicedesk/apps.py:

# servicedesk/apps.py
# from django.apps import AppConfig
# class ServicedeskConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'servicedesk'
#     def ready(self):
#         import servicedesk.signals # ou import servicedesk.models se os receivers estiverem aqui
#
# E em servicedesk/__init__.py, adicione:
# default_app_config = 'servicedesk.apps.ServicedeskConfig'
#
# Se você não fizer isso, os signals podem não ser conectados quando o Django iniciar.
# Uma forma mais simples, mas menos "moderna", é garantir que este models.py
# seja importado em algum momento, o que geralmente acontece.

