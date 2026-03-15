from django.db import models
from django.utils.text import slugify


class Service(models.Model):
    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(
        "Résumé",
        max_length=255,
        help_text="Petite phrase qui résume le service."
    )
    description = models.TextField("Description détaillée")
    icon = models.CharField(
        "Icône (optionnel)",
        max_length=100,
        blank=True,
        help_text="Nom d'icône Bootstrap/FontAwesome par ex."
    )
    image = models.ImageField(
        "Image illustrative",
        upload_to="services/",
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(
        "Ordre d'affichage",
        default=0
    )
    is_active = models.BooleanField("Actif ?", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
