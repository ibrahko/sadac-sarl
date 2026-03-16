from django.db import models
from apps.products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('processing', 'En cours'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
    ]
    UNIT_CHOICES = [
        ('kg', 'Kilogramme (kg)'),
        ('sac', 'Sac'),
        ('tonne', 'Tonne'),
        ('litre', 'Litre'),
        ('unite', 'Unité'),
    ]
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,
                                 null=True, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    unit       = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='kg',
        verbose_name="Unité"
    )
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                               default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Commande"

    def __str__(self):
        return f"{self.full_name} – {self.product}"
