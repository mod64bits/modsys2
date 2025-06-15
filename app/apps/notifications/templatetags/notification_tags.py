# notifications/templatetags/notification_tags.py
from django import template
from ..models import Notification

register = template.Library()

@register.inclusion_tag('notifications/includes/notification_dropdown.html', takes_context=True)
def notification_dropdown(context):
    user = context.get('user')
    if user and user.is_authenticated:
        # Obtém as 5 notificações mais recentes não lidas
        notifications = user.notifications.filter(read=False).order_by('-created_at')[:5]
        unread_count = user.notifications.filter(read=False).count()
    else:
        notifications = []
        unread_count = 0

    return {
        'notifications': notifications,
        'unread_count': unread_count
    }
