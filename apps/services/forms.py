from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ("title", "short_description", "description",
                  "icon", "image", "order", "is_active")
