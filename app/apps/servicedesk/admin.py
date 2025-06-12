# servicedesk/admin.py
from django.contrib import admin
from .models import Ticket, WorkOrder, Category

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'priority', 'created_by', 'assigned_to', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'created_at', 'assigned_to')
    search_fields = ('title', 'description', 'created_by__username', 'assigned_to__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Detalhes e Atribuição', {
            'fields': ('status', 'priority', 'assigned_to') # 'category'
        }),
        ('Informações do Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',) # Oculta por padrão
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Ao criar
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_info', 'status', 'assigned_technician', 'scheduled_date', 'completion_date', 'created_at')
    list_filter = ('status', 'assigned_technician', 'scheduled_date', 'completion_date')
    search_fields = ('ticket__title', 'description', 'assigned_technician__username')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['ticket'] # Para melhor seleção de ticket

    def ticket_info(self, obj):
        return f"#{obj.ticket.id} - {obj.ticket.title}"
    ticket_info.short_description = "Ticket Relacionado"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

