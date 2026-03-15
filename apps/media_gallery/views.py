# apps/media_gallery/views.py
from django.views.generic import ListView, DetailView
from .models import Gallery


class GalleryListView(ListView):
    model = Gallery
    template_name = "media_gallery/list.html"   # à créer
    context_object_name = "galleries"
    paginate_by = 12

    def get_queryset(self):
        return Gallery.objects.order_by(
            "-created_at"  # ← ajouter ordering
        )


class GalleryDetailView(DetailView):
    model = Gallery
    template_name = "media_gallery/album.html"  # à créer
    context_object_name = "gallery"
