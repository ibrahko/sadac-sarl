from django.db import models

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Abonné"

    def __str__(self):
        return self.email


class Newsletter(models.Model):
    STATUS_CHOICES = [('draft', 'Brouillon'), ('sent', 'Envoyée')]
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                               default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Newsletter"

    def __str__(self):
        return self.subject
