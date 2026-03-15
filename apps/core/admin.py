from django.contrib import admin
from .models import SiteSetting, Partner, ContactMessage


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone1", "whatsapp")
    fieldsets = (
        ("Identité", {"fields": ("name", "slogan", "description", "logo")}),
        ("Contact", {"fields": ("email", "phone1", "phone2",
                                "whatsapp", "address")}),
        ("Réseaux sociaux", {"fields": ("facebook_url", "youtube_url")}),
    )

    def has_add_permission(self, request):
        # un seul enregistrement
        return not SiteSetting.objects.exists()


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "phone", "subject", "message", "created_at")
