# financial/admin.py
from django.contrib import admin
from .models import ContaReceber, Pagamento

class PagamentoInline(admin.TabularInline):
    model = Pagamento
    extra = 0
    readonly_fields = ('created_at', 'registrado_por')
    fields = ('data_pagamento', 'valor_pago', 'metodo', 'registrado_por', 'created_at')

@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'descricao', 'valor_total', 'valor_pago', 'saldo_devedor', 'data_vencimento', 'status')
    list_filter = ('status', 'data_vencimento', 'cliente')
    search_fields = ('id', 'cliente__nome', 'descricao', 'orcamento_origem__id')
    readonly_fields = ('valor_pago', 'created_at', 'updated_at')
    inlines = [PagamentoInline]

    def save_formset(self, request, form, formset, change):
        # Ao salvar pagamentos pelo admin, garantir que o usuário seja registado
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk and isinstance(instance, Pagamento):
                instance.registrado_por = request.user
            instance.save()
        formset.save_m2m()
        # O signal já tratará de recalcular os totais
