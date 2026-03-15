from apps.orders.models import Order
from apps.core.models import ContactMessage


def backoffice_context(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    return {
        "new_orders_count": Order.objects.filter(status="new").count(),
        "unread_messages_count": ContactMessage.objects.filter(
            is_read=False).count(),
    }
