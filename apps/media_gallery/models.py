from django.db import models
from apps.events.models import Event

class Gallery(models.Model):
    event = models.ForeignKey(Event, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='galleries')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Galerie"

    def __str__(self):
        return self.title


class Media(models.Model):
    TYPE_CHOICES = [('image', 'Image'), ('video', 'Vidéo')]
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE,
                                 related_name='medias')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES,
                             default='image')
    file = models.ImageField(upload_to='gallery/', blank=True, null=True)
    url = models.URLField(blank=True, help_text="URL YouTube/Facebook")
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Média"

    def __str__(self):
        return f"{self.type} – {self.gallery.title}"
