import threading
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Subscriber, Newsletter


def send_newsletter(newsletter_id):
    try:
        newsletter = Newsletter.objects.get(id=newsletter_id)
    except Newsletter.DoesNotExist:
        return 0

    if newsletter.status == 'sent':
        return 0

    subscribers = Subscriber.objects.filter(is_active=True)
    count = subscribers.count()

    if count == 0:
        return 0

    # ← Marquer comme envoyée AVANT le thread
    # pour ne pas bloquer la réponse HTTP
    newsletter.status  = 'sent'
    newsletter.sent_at = timezone.now()
    newsletter.save()

    # Copie des données AVANT le thread
    # (évite les problèmes de context Django dans les threads)
    subject        = newsletter.subject
    body           = newsletter.body
    from_email     = settings.DEFAULT_FROM_EMAIL
    emails         = list(
        subscribers.values_list('email', flat=True)
    )

    # ← Envoi dans un thread séparé
    # La réponse HTTP est renvoyée immédiatement
    def send_all():
        for email in emails:
            try:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=from_email,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception:
                pass

    t = threading.Thread(target=send_all, daemon=True)
    t.start()

    return count
