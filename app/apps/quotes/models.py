# quotes/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from customers.models import Customer
from inventory.models import Produto
from django.contrib.auth.models import User


class Orcamento(models.Model):
    class StatusOrcamento(models.TextChoices):
        NAO_ENVIADO = 'NAO_ENVIADO', _('Não Enviado')
        EM_ANALISE = 'EM_ANALISE', _('Em Análise')
        APROVADO = 'APROVADO', _('Aprovado')
        REPROVADO = 'REPROVADO', _('Reprovado') # Renomeado de Não Aprovado para consistência
        CONCLUIDO = 'CONCLUIDO', _('Concluído') # Status adicional
        CANCELADO = 'CANCELADO', _('Cancelado') # Status adicional

    cliente = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT, # Evitar excluir cliente com orçamentos
        related_name='orcamentos',
        verbose_name=_("Cliente")
    )
    validade = models.DateField(
        verbose_name=_("Validade da Proposta"),
        null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=StatusOrcamento.choices,
        default=StatusOrcamento.NAO_ENVIADO,
        verbose_name=_("Status")
    )
    descricao_geral = models.TextField(
        blank=True, null=True,
        verbose_name=_("Descrição Geral/Observações do Orçamento")
    )

    # Campos calculados (serão atualizados por signals ou métodos)
    total_produtos_compra = models.DecimalField(
        max_digits=16, decimal_places=2, default=Decimal('0.00'),
        verbose_name=_("Custo Total Produtos")
    )
    total_produtos_venda = models.DecimalField(
        max_digits=16, decimal_places=2, default=Decimal('0.00'),
        verbose_name=_("Venda Total Produtos")
    )
    total_mao_de_obra = models.DecimalField(
        max_digits=16, decimal_places=2, default=Decimal('0.00'),
        verbose_name=_("Total Mão de Obra")
    )
    total_insumos = models.DecimalField( # Gastos/Insumos
        max_digits=16, decimal_places=2, default=Decimal('0.00'),
        verbose_name=_("Total Insumos/Gastos Adicionais")
    )
    valor_total_orcamento = models.DecimalField(
        max_digits=16, decimal_places=2, default=Decimal('0.00'),
        verbose_name=_("Valor Total do Orçamento")
    )

    # Lucratividade (calculada)
    lucro_equipamentos = models.DecimalField(
        max_digits=16, decimal_places=2, default=Decimal('0.00'),
        verbose_name=_("Lucro Equipamentos (Venda - Custo)")
    )
    lucro_total_bruto = models.DecimalField( # Lucro antes de descontar insumos/gastos
        max_digits=16, decimal_places=2, default=Decimal('0.00'),
        verbose_name=_("Lucro Total Bruto (Venda Prod. + M.O. - Custo Prod.)")
    )
    lucro_total_liquido = models.DecimalField( # Lucro final
        max_digits=16, decimal_places=2, default=Decimal('0.00'),
        verbose_name=_("Lucro Total Líquido (Após Insumos)")
    )

    # Datas e usuário
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='orcamentos_criados',
        verbose_name=_("Criado por")
    )

    def __str__(self):
        return f"Orçamento #{self.pk} - {self.cliente.nome} ({self.get_status_display()})"

    def recalcular_totais(self):
        """Recalcula todos os totais do orçamento com base nos seus itens."""

        # Totais de Produtos
        soma_compra_produtos = Decimal('0.00')
        soma_venda_produtos = Decimal('0.00')
        for item_produto in self.itens_produto.all():
            soma_compra_produtos += item_produto.get_subtotal_compra()
            soma_venda_produtos += item_produto.get_subtotal_venda()

        self.total_produtos_compra = soma_compra_produtos
        self.total_produtos_venda = soma_venda_produtos
        self.lucro_equipamentos = self.total_produtos_venda - self.total_produtos_compra

        # Total Mão de Obra
        soma_mao_de_obra = Decimal('0.00')
        for item_mao_obra in self.itens_mao_de_obra.all():
            soma_mao_de_obra += item_mao_obra.valor
        self.total_mao_de_obra = soma_mao_de_obra

        # Total Insumos
        soma_insumos = Decimal('0.00')
        for insumo in self.insumos_orcamento.all():
            soma_insumos += insumo.valor
        self.total_insumos = soma_insumos

        # Valor Total Orçamento e Lucros
        self.valor_total_orcamento = self.total_produtos_venda + self.total_mao_de_obra
        self.lucro_total_bruto = (self.total_produtos_venda + self.total_mao_de_obra) - self.total_produtos_compra
        self.lucro_total_liquido = self.lucro_total_bruto - self.total_insumos

        self.save(update_fields=[
            'total_produtos_compra', 'total_produtos_venda', 'lucro_equipamentos',
            'total_mao_de_obra', 'total_insumos', 'valor_total_orcamento',
            'lucro_total_bruto', 'lucro_total_liquido', 'updated_at'
        ])

    class Meta:
        verbose_name = _("Orçamento")
        verbose_name_plural = _("Orçamentos")
        ordering = ['-created_at']


class ItemProdutoOrcamento(models.Model):
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name='itens_produto',
        verbose_name=_("Orçamento")
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT, # Evitar excluir produto usado em orçamentos
        verbose_name=_("Produto")
    )
    quantidade = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_("Quantidade")
    )
    # Preço de compra no momento da adição ao orçamento (para histórico)
    preco_compra_unitario_historico = models.DecimalField(
        max_digits=16, decimal_places=2,
        verbose_name=_("Preço de Compra Unit. (Histórico)")
    )
    # Preço de venda pode ser calculado por margem ou definido manualmente
    preco_venda_unitario_definido = models.DecimalField(
        max_digits=16, decimal_places=2,
        verbose_name=_("Preço de Venda Unit. (Definido)")
    )
    # Ou usar uma porcentagem de markup sobre o preço de compra
    porcentagem_markup = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_("Markup (%)"),
        help_text=_("Se preenchido, calcula o preço de venda sobre o preço de compra. Ex: 20 para 20%.")
    )

    def get_preco_venda_unitario_calculado(self):
        if self.porcentagem_markup is not None and self.porcentagem_markup > 0:
            return self.preco_compra_unitario_historico * (1 + (self.porcentagem_markup / Decimal('100.0')))
        return self.preco_venda_unitario_definido

    def get_subtotal_compra(self):
        return self.quantidade * self.preco_compra_unitario_historico

    def get_subtotal_venda(self):
        return self.quantidade * self.get_preco_venda_unitario_calculado()

    def get_lucro_item(self):
        return self.get_subtotal_venda() - self.get_subtotal_compra()

    def save(self, *args, **kwargs):
        # Ao salvar, se o preço de compra histórico não estiver definido, pega do produto
        if not self.pk and self.produto and not self.preco_compra_unitario_historico: # Apenas na criação
             self.preco_compra_unitario_historico = self.produto.preco_compra
        # Se o preço de venda definido não estiver preenchido e o markup sim, calcula
        if not self.preco_venda_unitario_definido and self.porcentagem_markup is not None:
            self.preco_venda_unitario_definido = self.get_preco_venda_unitario_calculado()
        # Se nem venda nem markup, e produto tem preço de venda sugerido, usa ele
        elif not self.preco_venda_unitario_definido and self.produto and self.produto.preco_venda_sugerido:
             self.preco_venda_unitario_definido = self.produto.preco_venda_sugerido

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome} no Orçamento #{self.orcamento.pk}"

    class Meta:
        verbose_name = _("Item de Produto do Orçamento")
        verbose_name_plural = _("Itens de Produtos do Orçamento")
        unique_together = ('orcamento', 'produto') # Evitar duplicar produto no mesmo orçamento

class MaoDeObraOrcamento(models.Model):
    TIPO_CHOICES = [
        ('INSTALACAO', _('Instalação')),
        ('MANUTENCAO', _('Manutenção')),
        ('CONFIGURACAO', _('Configuração')),
        ('CONSULTORIA', _('Consultoria')),
        ('OUTRO', _('Outro')),
    ]
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name='itens_mao_de_obra',
        verbose_name=_("Orçamento")
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='OUTRO',
        verbose_name=_("Tipo de Serviço")
    )
    descricao = models.CharField(max_length=255, verbose_name=_("Descrição do Serviço"))
    valor = models.DecimalField(
        max_digits=16, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_("Valor")
    )

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.descricao} (R$ {self.valor}) no Orçamento #{self.orcamento.pk}"

    class Meta:
        verbose_name = _("Item de Mão de Obra do Orçamento")
        verbose_name_plural = _("Itens de Mão de Obra do Orçamento")

class InformacoesOrcamento(models.Model): # Informações adicionais, 1-para-1 com Orçamento
    orcamento = models.OneToOneField(
        Orcamento,
        on_delete=models.CASCADE,
        related_name='informacoes_adicionais',
        primary_key=True,
        verbose_name=_("Orçamento")
    )
    condicoes_pagamento = models.TextField(blank=True, null=True, verbose_name=_("Condições de Pagamento"))
    prazo_entrega_instalacao = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Prazo de Entrega/Instalação"))
    garantia = models.TextField(blank=True, null=True, verbose_name=_("Termos de Garantia"))
    # Outros campos que podem ser úteis:
    # local_servico = models.TextField(blank=True, null=True, verbose_name=_("Local da Prestação do Serviço"))
    # contato_responsavel_cliente = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Contato Responsável no Cliente"))

    def __str__(self):
        return f"Informações Adicionais do Orçamento #{self.orcamento.pk}"

    class Meta:
        verbose_name = _("Informação Adicional do Orçamento")
        verbose_name_plural = _("Informações Adicionais do Orçamento")

class InsumoOrcamento(models.Model): # Gastos/Insumos
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name='insumos_orcamento',
        verbose_name=_("Orçamento")
    )
    descricao = models.CharField(max_length=255, verbose_name=_("Descrição do Insumo/Gasto"))
    valor = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_("Valor do Insumo/Gasto")
    )
    data_gasto = models.DateField(default=timezone.now, verbose_name=_("Data do Gasto"))

    def __str__(self):
        return f"{self.descricao} (R$ {self.valor}) para Orçamento #{self.orcamento.pk}"

    class Meta:
        verbose_name = _("Insumo/Gasto do Orçamento")
        verbose_name_plural = _("Insumos/Gastos do Orçamento")
        ordering = ['-data_gasto']


# Signals para recalcular totais do orçamento quando itens são salvos ou excluídos
@receiver([post_save, post_delete], sender=ItemProdutoOrcamento)
@receiver([post_save, post_delete], sender=MaoDeObraOrcamento)
@receiver([post_save, post_delete], sender=InsumoOrcamento)
def atualizar_totais_orcamento_signal(sender, instance, **kwargs):
    # 'instance' é o ItemProdutoOrcamento, MaoDeObraOrcamento ou InsumoOrcamento
    # Precisamos acessar o orçamento relacionado a ele.
    orcamento_afetado = instance.orcamento
    if orcamento_afetado:
        orcamento_afetado.recalcular_totais()

