from django import forms
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage


# Mots-clés spam courants
SPAM_KEYWORDS = [
    'seo', 'google search', 'backlink', 'boost your',
    'index your', 'rank your', 'search engine',
    'crypto', 'bitcoin', 'investment', 'loan',
    'click here', 'rocketdigital', 'domains@',
    'affordable', 'best price', 'limited offer',
    'free trial', 'make money',
]


class ContactForm(forms.ModelForm):

    # Champ honeypot invisible pour les bots
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        label=""
    )

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "phone",
                  "subject", "message")

    def clean(self):
        cleaned_data = super().clean()

        # Si le honeypot est rempli → bot détecté
        if cleaned_data.get("website"):
            raise forms.ValidationError("Spam détecté.")

        # Filtre mots-clés spam
        message = cleaned_data.get("message", "").lower()
        subject = cleaned_data.get("subject", "").lower()
        name    = cleaned_data.get("name", "").lower()

        for keyword in SPAM_KEYWORDS:
            if (keyword in message or
                    keyword in subject or
                    keyword in name):
                raise forms.ValidationError(
                    "Votre message a été identifié "
                    "comme indésirable."
                )

        return cleaned_data

    def save(self, commit=True):
        obj = super().save(commit=commit)
        return obj

    def send_email(self):
        data = self.cleaned_data
        subject = f"[Contact SADAC] {data['subject']}"
        body = (
            f"Nom : {data['name']}\n"
            f"Email : {data['email']}\n"
            f"Téléphone : {data['phone']}\n\n"
            f"Message :\n{data['message']}"
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.SADAC_EMAIL],
            fail_silently=True,
        )
