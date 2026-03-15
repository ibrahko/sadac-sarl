from django import forms
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "phone", "subject", "message")

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
