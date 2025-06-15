# notifications/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def mark_as_read(request):
    """
    View para marcar notificações como lidas.
    Pode marcar todas ou apenas uma específica com base nos dados do POST.
    """
    if request.method == 'POST':
        notification_id = request.POST.get('id', None)
        
        if notification_id:
            # Marcar uma notificação específica como lida
            try:
                notification = Notification.objects.get(pk=notification_id, recipient=request.user)
                notification.read = True
                notification.save()
                unread_count = request.user.notifications.filter(read=False).count()
                return JsonResponse({'success': True, 'unread_count': unread_count})
            except Notification.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Notificação não encontrada.'}, status=404)
        else:
            # Marcar todas as notificações como lidas
            request.user.notifications.filter(read=False).update(read=True)
            return JsonResponse({'success': True, 'unread_count': 0})
            
    return JsonResponse({'success': False, 'error': 'Pedido inválido.'}, status=400)

