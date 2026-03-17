from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
import threading


def send_email_async(subject, message, from_email, recipient_list):
    """Envoie l'email dans un thread séparé pour ne pas bloquer la requête"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=True,
        )
    except Exception:
        pass


@receiver(post_save, sender=Order)
def send_order_emails(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        unit = instance.get_unit_display()
    except Exception:
        unit = ""

    # Email à SADAC — envoi asynchrone
    t1 = threading.Thread(
        target=send_email_async,
        args=(
            f"Nouvelle commande : {instance.product}",
            f"""
Nom       : {instance.full_name}
Téléphone : {instance.phone}
Email     : {instance.email}
Produit   : {instance.product}
Quantité  : {instance.quantity} {unit}
Message   : {instance.message}
            """,
            settings.DEFAULT_FROM_EMAIL,
            [settings.SADAC_EMAIL],
        ),
        daemon=True,
    )
    t1.start()

    # Email au client — envoi asynchrone
    if instance.email:
        t2 = threading.Thread(
            target=send_email_async,
            args=(
                "Votre demande a bien été reçue – SADAC SARL",
                f"""
Bonjour {instance.full_name},

Nous avons bien reçu votre demande pour :
Produit  : {instance.product}
Quantité : {instance.quantity} {unit}

Notre équipe vous contactera très bientôt.

Cordialement,
L'équipe SADAC SARL
                """,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
            ),
            daemon=True,
        )
        t2.start()
