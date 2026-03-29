from django.core.mail import get_connection, EmailMessage
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

    # Marquer comme envoyée immédiatement
    newsletter.status  = 'sent'
    newsletter.sent_at = timezone.now()
    newsletter.save()

    emails = list(
        subscribers.values_list('email', flat=True)
    )

    try:
        # Ouvrir une seule connexion SMTP
        # et envoyer tous les emails d'un coup
        connection = get_connection(
            fail_silently=True,
            timeout=30,
        )
        connection.open()

        messages = []
        for email in emails:
            msg = EmailMessage(
                subject=newsletter.subject,
                body=newsletter.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
                connection=connection,
            )
            messages.append(msg)

        if messages:
            connection.send_messages(messages)

        connection.close()

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Newsletter send error: {e}")

    return count
