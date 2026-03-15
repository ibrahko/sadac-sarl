from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('services/', include('apps.services.urls')),
    path('produits/', include('apps.products.urls')),
    path('evenements/', include('apps.events.urls')),
    path('galerie/', include('apps.media_gallery.urls')),
    path('actualites/', include('apps.blog.urls')),
    path('newsletter/', include('apps.newsletter.urls')),
    path('commandes/', include('apps.orders.urls')),
    path("backoffice/", include("apps.backoffice.urls")),
    path('accounts/', include('apps.accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
