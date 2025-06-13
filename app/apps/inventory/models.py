# inventory/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

class Fornecedor(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome do Fornecedor")
    documento = models.CharField(max_length=20, blank=True, null=True, verbose_name="Documento (CNPJ/CPF)")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="E-mail de Contato")

    endereco_logradouro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    endereco_numero = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número")
    endereco_complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    endereco_bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    endereco_cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    endereco_estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")
    endereco_cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']

class CategoriaProduto(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"
        ordering = ['nome']

class Produto(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome do Produto")
    fabricante = models.CharField(max_length=255, blank=True, null=True, verbose_name="Fabricante")
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Fornecedor Principal",
        related_name="produtos"
    )
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição Detalhada")

    preco_compra = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="Preço de Compra"
    )
    preco_venda_sugerido = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        blank=True, null=True,
        verbose_name="Preço de Venda Sugerido"
    )

    # Novo campo para controlo de stock
    quantidade_em_estoque = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        verbose_name=_("Quantidade em Stock")
    )

    categoria = models.ForeignKey(
        CategoriaProduto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoria",
        related_name="produtos"
    )

    codigo_barras = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name="Código de Barras")

    ativo = models.BooleanField(default=True, verbose_name="Produto Ativo?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome}{' (' + self.fabricante + ')' if self.fabricante else ''}"

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']
