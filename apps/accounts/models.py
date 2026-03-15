from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin_sadac', "Admin SADAC"),
        ('editor', "Rédacteur"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='editor'
    )
    phone = models.CharField(max_length=20, blank=True)
    job_title = models.CharField("Fonction", max_length=150, blank=True)

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"
