from django.urls import path
from .views import GalleryListView, GalleryDetailView

app_name = "media_gallery"

urlpatterns = [
    path("", GalleryListView.as_view(), name="list"),
    path("<int:pk>/", GalleryDetailView.as_view(), name="detail"),
]
