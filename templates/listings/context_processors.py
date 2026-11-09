from .models import PrivateMessage

def unread_messages_processor(request):
    if request.user.is_authenticated:
        count = PrivateMessage.objects.filter(
            recipient=request.user,
            is_read=False,
            is_blocked_by_ai=False
        ).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}