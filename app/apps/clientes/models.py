from django.db import models

# Create your models here.

class Cliente(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CPF', 'CPF'),
        ('CNPJ', 'CNPJ'),
    ]
    
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    documento = models.CharField(max_length=14, unique=True)
    tipo_documento = models.CharField(max_length=4, choices=TIPO_DOCUMENTO_CHOICES)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
