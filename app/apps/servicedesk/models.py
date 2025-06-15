# servicedesk/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.notifications.models import Notification
from django.db.models.signals import post_save, post_delete # Adicionar post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal

# Importar o modelo de Produto
from apps.inventory.models import Produto

def ticket_attachment_path(instance, filename):
    return f'tickets/{instance.comment.ticket.id}/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']

class Ticket(models.Model):
    # ... (modelo Ticket sem alterações) ...
    STATUS_CHOICES = [ ('ABERTO', 'Aberto'), ('EM_ANDAMENTO', 'Em Andamento'), ('AGUARDANDO_CLIENTE', 'Aguardando Cliente'), ('RESOLVIDO', 'Resolvido'), ('FECHADO', 'Fechado'), ]
    PRIORITY_CHOICES = [ ('BAIXA', 'Baixa'), ('MEDIA', 'Média'), ('ALTA', 'Alta'), ('URGENTE', 'Urgente'), ]
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição Detalhada")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO', verbose_name="Status")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIA', verbose_name="Prioridade")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria", related_name='tickets')
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente", related_name='tickets')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tickets', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Criado Por")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_tickets', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Atribuído Para")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    def __str__(self): return f"#{self.id} - {self.title}"
    class Meta: verbose_name = "Ticket"; verbose_name_plural = "Tickets"; ordering = ['-created_at']

class TicketComment(models.Model):
    # ... (modelo TicketComment sem alterações) ...
    class CommentType(models.TextChoices): COMMENT = 'COMMENT', _('Comentário'); LOG = 'LOG', _('Registo de Atividade')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments', verbose_name=_("Ticket"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Autor"), help_text=_("Se nulo, é um registo do sistema."))
    comment = models.TextField(verbose_name=_("Comentário / Atividade"))
    comment_type = models.CharField(max_length=10, choices=CommentType.choices, default=CommentType.COMMENT, verbose_name=_("Tipo"))
    is_internal_note = models.BooleanField(default=False, verbose_name=_("É uma nota interna?"), help_text=_("Notas internas são visíveis apenas para a equipa."))
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): author_name = self.author.get_full_name() if self.author and self.author.get_full_name() else (self.author.username if self.author else "Sistema"); return f'Comentário de {author_name} no ticket #{self.ticket.id}'
    class Meta: verbose_name = "Comentário de Ticket"; verbose_name_plural = "Comentários de Tickets"; ordering = ['created_at']

class Attachment(models.Model):
    # ... (modelo Attachment sem alterações) ...
    comment = models.ForeignKey(TicketComment, on_delete=models.CASCADE, related_name='attachments', verbose_name=_("Comentário Associado"))
    file = models.FileField(upload_to=ticket_attachment_path, verbose_name=_("Ficheiro"))
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_("Enviado por"))
    def __str__(self): return self.file.name.split('/')[-1]

    @property
    def filename(self): return self.file.name.split('/')[-1]

    @property
    def filesize(self):
        try: return f"{self.file.size / 1024:.2f} KB";
        except (OSError, FileNotFoundError): return "0 KB"

class WorkOrder(models.Model):
    # ... (modelo WorkOrder com novo campo `orcamento_origem`) ...
    STATUS_CHOICES = [ ('PENDENTE', 'Pendente'), ('AGENDADA', 'Agendada'), ('EM_EXECUCAO', 'Em Execução'), ('CONCLUIDA', 'Concluída'), ('CANCELADA', 'Cancelada'), ]
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='work_orders', verbose_name="Ticket Relacionado")
    orcamento_origem = models.ForeignKey(
        'quotes.Orcamento',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ordens_de_servico_geradas',
        verbose_name="Orçamento de Origem"
    )
    description = models.TextField(verbose_name="Descrição dos Serviços")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status da OS")
    assigned_technician = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_work_orders', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Técnico Responsável")
    scheduled_date = models.DateTimeField(null=True, blank=True, verbose_name="Data Agendada")
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão")
    notes = models.TextField(blank=True, null=True, verbose_name="Observações Internas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação da OS")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização da OS")
    def __str__(self): return f"OS #{self.id} para Ticket #{self.ticket.id}"
    @property
    def customer(self): return self.ticket.customer
    class Meta: verbose_name = "Ordem de Serviço"; verbose_name_plural = "Ordens de Serviço"; ordering = ['-created_at']

# Novo Modelo para ligar Produtos a uma Ordem de Serviço
class ProdutoUtilizadoOS(models.Model):
    ordem_de_servico = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='produtos_utilizados',
        verbose_name="Ordem de Serviço"
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='utilizado_em_os',
        verbose_name="Produto"
    )
    quantidade = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_("Quantidade Utilizada")
    )
    # Guardar preços no momento da utilização para histórico de custos preciso
    preco_compra_no_momento = models.DecimalField(max_digits=16, decimal_places=2, help_text="Custo do produto no momento em que foi adicionado à OS.")
    preco_venda_no_momento = models.DecimalField(max_digits=16, decimal_places=2, help_text="Preço de venda praticado no momento.")

    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome} em OS #{self.ordem_de_servico.id}"

    class Meta:
        verbose_name = "Produto Utilizado em OS"
        verbose_name_plural = "Produtos Utilizados em OS"
        unique_together = ('ordem_de_servico', 'produto')


# Signals para atualizar o stock quando um produto é utilizado/removido de uma OS
@receiver(post_save, sender=ProdutoUtilizadoOS)
def atualizar_stock_ao_adicionar_produto(sender, instance, created, **kwargs):
    """Deduz a quantidade do stock do produto quando um item é criado na OS."""
    if created: # Executa apenas na criação do registo
        produto = instance.produto
        produto.quantidade_em_estoque -= instance.quantidade
        produto.save(update_fields=['quantidade_em_estoque'])

@receiver(post_delete, sender=ProdutoUtilizadoOS)
def atualizar_stock_ao_remover_produto(sender, instance, **kwargs):
    """Devolve a quantidade ao stock do produto quando um item é removido da OS."""
    produto = instance.produto
    produto.quantidade_em_estoque += instance.quantidade
    produto.save(update_fields=['quantidade_em_estoque'])

@receiver(post_save, sender=Ticket)
def create_ticket_notification(sender, instance, created, **kwargs):
    """
    Cria uma notificação quando um ticket é atribuído a um utilizador.
    """
    # Verifica se o campo 'assigned_to' foi definido e se não é uma nova criação de ticket
    # (para não notificar na criação, apenas na atribuição/alteração)
    if not created and instance.assigned_to:
        # Para ser mais preciso, devemos verificar se o campo 'assigned_to' mudou.
        # A forma mais simples de o fazer é no form/view, mas aqui podemos fazer uma verificação básica.
        # A lógica mais robusta seria guardar o estado anterior.
        # Por agora, vamos notificar se o ticket for guardado e tiver alguém atribuído.

        # Evitar notificar o próprio utilizador que fez a alteração
        try:
            # A view precisa de definir request.user no objeto antes de o guardar para isto funcionar
            if hasattr(instance, '_current_user') and instance._current_user == instance.assigned_to:
                return
        except:
            pass

        # Cria a notificação
        Notification.objects.create(
            recipient=instance.assigned_to,
            message=f"O Ticket #{instance.id} - '{instance.title[:30]}...' foi-lhe atribuído.",
            link=reverse('servicedesk:ticket_list') # Exemplo de link, pode ser mais específico
        )
