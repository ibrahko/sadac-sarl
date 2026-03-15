from django import forms
from .models import Subscriber

class NewsletterSubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ("email", "name")
