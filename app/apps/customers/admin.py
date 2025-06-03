# customers/admin.py
from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'tipo_documento', 'documento', 'email', 'telefone',
        'tipo_cliente', 'usuario_sistema', 'created_at'
    )
    list_filter = ('tipo_cliente', 'tipo_documento', 'criar_usuario_sistema', 'endereco_estado')
    search_fields = ('nome', 'documento', 'email', 'telefone', 'usuario_sistema__username')
    readonly_fields = ('created_at', 'updated_at', 'usuario_sistema') # Torna usuario_sistema readonly no admin, pois é gerenciado pelo signal

    fieldsets = (
        ('Informações Pessoais/Empresariais', {
            'fields': ('nome', 'tipo_documento', 'documento', 'email', 'telefone', 'tipo_cliente')
        }),
        ('Endereço', {
            'fields': ('endereco_logradouro', 'endereco_numero', 'endereco_complemento', 'endereco_bairro', 'endereco_cidade', 'endereco_estado', 'endereco_cep'),
            'classes': ('collapse',) # Opcional, para agrupar e ocultar
        }),
        ('Acesso ao Sistema', {
            'fields': ('criar_usuario_sistema', 'usuario_sistema')
        }),
        ('Datas de Controle', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Se você quiser que o campo 'usuario_sistema' seja editável, remova-o de readonly_fields
    # e considere como isso interage com o signal. Geralmente, é melhor deixar o signal cuidar disso.
