from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("full_name", "product", "quantity",
                    "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "phone", "email", "product__title")
    readonly_fields = ("created_at",)
    list_editable = ("status",)
