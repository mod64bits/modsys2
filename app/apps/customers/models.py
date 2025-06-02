# customers/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class Customer(models.Model):
    class TipoDocumento(models.TextChoices):
        CPF = 'CPF', _('CPF')
        CNPJ = 'CNPJ', _('CNPJ')
        OUTRO = 'OUTRO', _('Outro') # Caso não seja CPF/CNPJ

    class TipoCliente(models.TextChoices):
        COMODATO = 'COMODATO', _('Comodato')
        CONTRATO = 'CONTRATO', _('Contrato')
        AVULSO = 'AVULSO', _('Avulso')

    # Informações básicas
    nome = models.CharField(max_length=255, verbose_name="Nome Completo / Razão Social")
    tipo_documento = models.CharField(
        max_length=5,
        choices=TipoDocumento.choices,
        default=TipoDocumento.CPF,
        verbose_name="Tipo de Documento"
    )
    documento = models.CharField(max_length=20, unique=True, verbose_name="Documento (CPF/CNPJ)") # Máscara será aplicada no frontend/forms
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone") # Máscara no frontend
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True, verbose_name="E-mail Principal")

    tipo_cliente = models.CharField(
        max_length=10,
        choices=TipoCliente.choices,
        default=TipoCliente.AVULSO,
        verbose_name="Tipo de Cliente"
    )

    # Endereço (simplificado, pode ser expandido para campos estruturados)
    endereco_logradouro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    endereco_numero = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número")
    endereco_complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    endereco_bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    endereco_cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    endereco_estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF") # Ex: SP, RJ
    endereco_cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP") # Máscara no frontend

    # Usuário do sistema para o cliente (opcional)
    criar_usuario_sistema = models.BooleanField(default=False, verbose_name="Criar acesso ao sistema para este cliente?")
    usuario_sistema = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_profile',
        verbose_name="Usuário de Acesso do Cliente"
    )
    # Campo para armazenar uma senha temporária se o usuário for criado automaticamente
    # A senha real deve ser definida pelo usuário ou por um processo de reset.
    # Este campo é mais para controle interno e não deve ser exibido diretamente.
    # senha_temporaria_usuario = models.CharField(max_length=128, blank=True, null=True, editable=False)


    # Datas de controle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_documento_display()}: {self.documento})"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']

# Signal para criar/atualizar usuário do sistema para o cliente
@receiver(post_save, sender=Customer)
def customer_post_save_receiver(sender, instance, created, **kwargs):
    """
    Cria ou atualiza um usuário do sistema para o cliente se solicitado.
    """
    customer = instance
    if customer.criar_usuario_sistema:
        if not customer.usuario_sistema:
            # Tenta encontrar um usuário existente pelo e-mail do cliente ou pelo documento formatado como username
            # Esta lógica de username pode precisar de ajustes para garantir unicidade e formato válido.
            username_candidate_email = customer.email.split('@')[0] if customer.email else None
            username_candidate_doc = "".join(filter(str.isdigit, customer.documento)) # Apenas números do documento

            user = None
            if customer.email:
                user = User.objects.filter(email=customer.email).first()

            if not user and username_candidate_email: # Tenta pelo nome de usuário derivado do email
                 if not User.objects.filter(username=username_candidate_email).exists():
                    user_to_create_username = username_candidate_email
                 elif not User.objects.filter(username=username_candidate_doc).exists(): # Tenta pelo documento se o do email já existir
                    user_to_create_username = username_candidate_doc
                 else: # Se ambos existirem, adiciona um sufixo ao do documento
                    user_to_create_username = f"{username_candidate_doc}_{customer.id}"

            elif not user and username_candidate_doc: # Se não tem email, tenta pelo documento
                if not User.objects.filter(username=username_candidate_doc).exists():
                    user_to_create_username = username_candidate_doc
                else:
                    user_to_create_username = f"{username_candidate_doc}_{customer.id}"
            else: # Se não conseguiu gerar um username único ou não tem email/documento, não cria
                # Log ou mensagem de erro aqui seria útil
                print(f"Não foi possível gerar um nome de usuário único para o cliente {customer.nome}.")
                return


            if not user: # Se não encontrou usuário existente, cria um novo
                user = User.objects.create_user(
                    username=user_to_create_username,
                    email=customer.email,
                    first_name=customer.nome.split(' ')[0], # Primeiro nome
                    last_name=' '.join(customer.nome.split(' ')[1:]) if len(customer.nome.split(' ')) > 1 else '' # Sobrenome
                )
                # Define uma senha padrão inicial (o usuário DEVE alterá-la)
                # Em um sistema real, envie um link de definição de senha.
                # Por simplicidade, vamos gerar uma senha aleatória simples.
                # NÃO FAÇA ISSO EM PRODUÇÃO SEM UM MECANISMO SEGURO DE ENTREGA/RESET DE SENHA.
                # temp_password = User.objects.make_random_password(length=10)
                # user.set_password(temp_password)
                # user.save()
                # customer.senha_temporaria_usuario = temp_password # Apenas para referência, NÃO EXIBA
                # print(f"Usuário {user.username} criado com senha temporária: {temp_password}")
                # Idealmente, você marcaria o usuário para forçar a troca de senha no primeiro login.

            customer.usuario_sistema = user
            # Evita recursão ao salvar o customer novamente dentro do signal
            # Desconecta temporariamente o signal, salva e reconecta, ou usa um atributo de flag.
            # Para este exemplo, vamos assumir que salvar apenas o campo usuario_sistema não vai causar problemas profundos de recursão.
            # No entanto, a melhor prática é ser mais cuidadoso.
            Customer.objects.filter(pk=customer.pk).update(usuario_sistema=user) # Salva sem chamar o signal novamente

        else: # Se já existe um usuário_sistema, apenas atualiza os dados se necessário
            user = customer.usuario_sistema
            changed = False
            if user.email != customer.email and customer.email:
                user.email = customer.email
                changed = True
            # Atualizar nome/sobrenome se desejar
            # if user.first_name != customer.nome.split(' ')[0] or user.last_name != ' '.join(customer.nome.split(' ')[1:]):
            #   user.first_name = customer.nome.split(' ')[0]
            #   user.last_name = ' '.join(customer.nome.split(' ')[1:]) if len(customer.nome.split(' ')) > 1 else ''
            #   changed = True
            if changed:
                user.save(update_fields=['email']) # Adicione 'first_name', 'last_name' se os atualizar

    elif customer.usuario_sistema and not customer.criar_usuario_sistema:
        # Se 'criar_usuario_sistema' for desmarcado e existe um usuário,
        # você pode optar por desativar o usuário ou apenas desassociá-lo.
        # Desassociar:
        # customer.usuario_sistema.is_active = False # Exemplo de desativação
        # customer.usuario_sistema.save(update_fields=['is_active'])
        # customer.usuario_sistema = None # Desassocia
        # Customer.objects.filter(pk=customer.pk).update(usuario_sistema=None)
        # A decisão aqui depende da regra de negócio. Por ora, vamos apenas desassociar.
        # IMPORTANTE: Considere o que acontece se este usuário for usado em outros lugares.
        # Apenas desassociar pode ser mais seguro do que desativar/excluir.
        user_to_disassociate = customer.usuario_sistema
        Customer.objects.filter(pk=customer.pk).update(usuario_sistema=None)
        # Opcional: Desativar o usuário se ele não tiver mais nenhum outro vínculo importante
        # if not user_to_disassociate.customer_profile_set.exists() and not user_to_disassociate.is_staff:
        #    user_to_disassociate.is_active = False
        #    user_to_disassociate.save()


# Conecte os signals (se não estiver usando apps.py ready())
# Esta linha não é estritamente necessária se o apps.py estiver configurado,
# mas não prejudica.
# post_save.connect(customer_post_save_receiver, sender=Customer)
