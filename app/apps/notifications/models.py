# notifications/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_("Destinatário")
    )
    message = models.CharField(max_length=255, verbose_name=_("Mensagem"))
    # URL para onde o utilizador será redirecionado ao clicar
    link = models.URLField(max_length=255, blank=True, null=True, verbose_name=_("Link"))
    read = models.BooleanField(default=False, verbose_name=_("Lida"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificação para {self.recipient.username}: {self.message}"

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-created_at']

