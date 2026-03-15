from django.views.generic import ListView, DetailView
from .models import Event

class EventListView(ListView):
    model = Event
    template_name = "events/list.html"
    context_object_name = "events"

    def get_queryset(self):
        status = self.request.GET.get("statut")
        qs = Event.objects.all()
        if status in ["upcoming", "past"]:
            qs = qs.filter(status=status)
        return qs.order_by("-start_date")


class EventDetailView(DetailView):
    model = Event
    template_name = "events/detail.html"
    context_object_name = "event"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Galeries liées à cet événement
        ctx["galleries"] = self.object.galleries.all()
        # Autres événements sauf celui en cours
        ctx["other_events"] = Event.objects.exclude(
            pk=self.object.pk
        ).order_by("-start_date")[:4]
        return ctx

