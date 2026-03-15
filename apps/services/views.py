from django.views.generic import ListView, DetailView
from .models import Service

class ServiceListView(ListView):
    model = Service
    template_name = "services/list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.filter(is_active=True).order_by("order")


class ServiceDetailView(DetailView):
    model = Service
    template_name = "services/detail.html"
    context_object_name = "service"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Autres services sauf celui en cours
        ctx["other_services"] = Service.objects.filter(
            is_active=True
        ).exclude(pk=self.object.pk).order_by("order")[:5]
        return ctx