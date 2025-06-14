# financial/models.py
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings

from apps.customers.models import Customer
from apps.quotes.models import Orcamento

class ContaReceber(models.Model):
    class StatusConta(models.TextChoices):
        PENDENTE = 'PENDENTE', _('Pendente')
        PAGO_PARCIALMENTE = 'PAGO_PARCIALMENTE', _('Pago Parcialmente')
        PAGO = 'PAGO', _('Pago')
        VENCIDO = 'VENCIDO', _('Vencido')
        CANCELADO = 'CANCELADO', _('Cancelado')

    cliente = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='contas_a_receber', verbose_name="Cliente")
    orcamento_origem = models.OneToOneField(
        Orcamento,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='conta_a_receber',
        verbose_name="Orçamento de Origem"
    )
    descricao = models.CharField(max_length=255, verbose_name="Descrição da Fatura")
    valor_total = models.DecimalField(
        max_digits=16, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor Total"
    )
    valor_pago = models.DecimalField(
        max_digits=16, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor Pago"
    )
    data_emissao = models.DateField(default=timezone.now, verbose_name="Data de Emissão")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    status = models.CharField(
        max_length=20,
        choices=StatusConta.choices,
        default=StatusConta.PENDENTE,
        verbose_name="Status"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fatura #{self.pk} - {self.cliente.nome} (R$ {self.valor_total})"

    @property
    def saldo_devedor(self):
        return self.valor_total - self.valor_pago

    def recalcular_e_atualizar_status(self):
        """Recalcula o valor pago e atualiza o status da conta."""
        total_pago = self.pagamentos.aggregate(total=Sum('valor_pago'))['total'] or Decimal('0.00')
        self.valor_pago = total_pago

        if self.status == self.StatusConta.CANCELADO:
            pass # Não altera status de contas canceladas
        elif self.valor_pago >= self.valor_total:
            self.status = self.StatusConta.PAGO
        elif self.valor_pago > 0:
            self.status = self.StatusConta.PAGO_PARCIALMENTE
        else:
            self.status = self.StatusConta.PENDENTE

        # Verifica se está vencida (e não paga/cancelada)
        if self.data_vencimento < timezone.now().date() and self.status in [self.StatusConta.PENDENTE, self.StatusConta.PAGO_PARCIALMENTE]:
            self.status = self.StatusConta.VENCIDO

        self.save(update_fields=['valor_pago', 'status', 'updated_at'])

    class Meta:
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"
        ordering = ['-data_vencimento']

class Pagamento(models.Model):
    class MetodoPagamento(models.TextChoices):
        PIX = 'PIX', _('PIX')
        BOLETO = 'BOLETO', _('Boleto Bancário')
        CARTAO_CREDITO = 'CARTAO_CREDITO', _('Cartão de Crédito')
        CARTAO_DEBITO = 'CARTAO_DEBITO', _('Cartão de Débito')
        TRANSFERENCIA = 'TRANSFERENCIA', _('Transferência Bancária')
        DINHEIRO = 'DINHEIRO', _('Dinheiro')
        OUTRO = 'OUTRO', _('Outro')

    conta = models.ForeignKey(
        ContaReceber,
        on_delete=models.CASCADE,
        related_name='pagamentos',
        verbose_name="Conta a Receber"
    )
    valor_pago = models.DecimalField(
        max_digits=16, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor Pago"
    )
    data_pagamento = models.DateField(default=timezone.now, verbose_name="Data do Pagamento")
    metodo = models.CharField(
        max_length=20,
        choices=MetodoPagamento.choices,
        default=MetodoPagamento.OUTRO,
        verbose_name="Método de Pagamento"
    )
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pagamento de R$ {self.valor_pago} para a Fatura #{self.conta.pk}"

    class Meta:
        verbose_name = "Registo de Pagamento"
        verbose_name_plural = "Registos de Pagamentos"
        ordering = ['-data_pagamento']

@receiver([post_save, post_delete], sender=Pagamento)
def atualizar_status_conta(sender, instance, **kwargs):
    """Signal para atualizar a conta a receber sempre que um pagamento é adicionado ou removido."""
    instance.conta.recalcular_e_atualizar_status()

