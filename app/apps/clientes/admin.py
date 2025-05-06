from django.contrib import admin
from .models import Cliente, Equipe


class EquipeInline(admin.TabularInline):  # Ou admin.StackedInline para uma exibição diferente
    model = Equipe.clientes.through  # Utilizamos o modelo de ligação gerado pelo ManyToMany
    extra = 0 # Quantidade de formulários extras exibidos na página


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'tipo_documento', 'documento')  # Campos exibidos na lista
    search_fields = ('nome', 'email', 'documento')  # Campos para busca
    list_filter = ('tipo_documento',)  # Filtro lateral
    inlines = [EquipeInline]  # Incluímos o inline relacionado

    def save_model(self, request, obj, form, change):
        """
        Adiciona lógica extra ao salvar o cliente, se necessário.
        """
        super().save_model(request, obj, form, change)


@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo')  # Campos exibidos na lista
    search_fields = ('nome', 'cargo')  # Campos para busca
    list_filter = ('cargo',)  # Filtro lateral
    filter_horizontal = ('clientes',)  # Exibe campo ManyToMany com uma interface amigável