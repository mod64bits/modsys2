from django.db import models
from apps.base.models import BaseModel

# Create your models here.

class Cliente(BaseModel):
    TIPO_DOCUMENTO_CHOICES = [
        ('CPF', 'CPF'),
        ('CNPJ', 'CNPJ'),
    ]
    
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    documento = models.CharField(max_length=30)
    tipo_documento = models.CharField(max_length=4, choices=TIPO_DOCUMENTO_CHOICES)


    def __str__(self):
        return self.nome

class Equipe(BaseModel):
    CARGO_CHOICES = [
        ('PROPRIETARIO', 'PROPRIETARIO'),
        ('GERENTE', 'GERENTE'),
        ('FUNCIONARIO', 'FUNCIONARIO'),
    ]
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=30, choices=CARGO_CHOICES)
    clientes = models.ManyToManyField(Cliente)

    def __str__(self):
        return f"{self.nome} - {self.cargo}"
