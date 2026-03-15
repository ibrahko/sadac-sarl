from django.contrib import admin
from .models import Subscriber, Newsletter
from .services import send_newsletter


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email", "name")
    list_editable = ("is_active",)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("subject", "status", "created_at", "sent_at")
    list_filter = ("status", "created_at")
    actions = ["send_selected_newsletters"]

    def send_selected_newsletters(self, request, queryset):
        count_total = 0
        for newsletter in queryset:
            count_total += send_newsletter(newsletter.id)
        self.message_user(
            request,
            f"{count_total} emails de newsletter envoyés."
        )
    send_selected_newsletters.short_description = "Envoyer les newsletters sélectionnées"
