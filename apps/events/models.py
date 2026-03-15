from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'À venir'),
        ('past', 'Passé'),
        ('cancelled', 'Annulé'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255)
    banner = models.ImageField(upload_to='events/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                               default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Événement"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Auto update status
        if self.start_date < timezone.now():
            self.status = 'past'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
