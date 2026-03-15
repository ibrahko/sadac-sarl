from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Post(models.Model):
    STATUS_CHOICES = [
        ("draft", "Brouillon"),
        ("published", "Publié"),
    ]

    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(
        "Image de couverture",
        upload_to="blog/",
        blank=True,
        null=True
    )
    excerpt = models.CharField(
        "Extrait",
        max_length=300,
        blank=True,
        help_text="Petit résumé qui s'affiche dans la liste."
    )
    content = models.TextField("Contenu")
    status = models.CharField(
        "Statut",
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts"
    )
    published_at = models.DateTimeField(
        "Date de publication",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
