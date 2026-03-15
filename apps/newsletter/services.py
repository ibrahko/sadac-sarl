from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Subscriber, Newsletter

def send_newsletter(newsletter_id):
    newsletter = Newsletter.objects.get(id=newsletter_id)
    if newsletter.status == 'sent':
        return 0

    subscribers = Subscriber.objects.filter(is_active=True)
    count = 0
    for sub in subscribers:
        send_mail(
            subject=newsletter.subject,
            message=newsletter.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sub.email],
            fail_silently=True,
        )
        count += 1

    newsletter.status = 'sent'
    newsletter.sent_at = timezone.now()
    newsletter.save()
    return count
