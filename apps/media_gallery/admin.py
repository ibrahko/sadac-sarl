from django.contrib import admin
from .models import Gallery, Media


class MediaInline(admin.TabularInline):
    model = Media
    extra = 1


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "created_at")
    list_filter = ("event",)
    inlines = [MediaInline]


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("gallery", "type", "caption", "order")
    list_filter = ("type", "gallery")
    list_editable = ("order",)
