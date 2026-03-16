from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order


@receiver(post_save, sender=Order)
def send_order_emails(sender, instance, created, **kwargs):
    if not created:
        return

    # Unité si le champ existe
    try:
        unit = instance.get_unit_display()
    except Exception:
        unit = ""

    try:
        # Email à SADAC
        send_mail(
            subject=f"Nouvelle commande : {instance.product}",
            message=f"""
Nom       : {instance.full_name}
Téléphone : {instance.phone}
Email     : {instance.email}
Produit   : {instance.product}
Quantité  : {instance.quantity} {unit}
Message   : {instance.message}
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.SADAC_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass

    try:
        # Email de confirmation au client
        if instance.email:
            send_mail(
                subject="Votre demande a bien été reçue – SADAC SARL",
                message=f"""
Bonjour {instance.full_name},

Nous avons bien reçu votre demande pour :
Produit  : {instance.product}
Quantité : {instance.quantity} {unit}

Notre équipe vous contactera très bientôt.

Cordialement,
L'équipe SADAC SARL
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )
    except Exception:
        pass
