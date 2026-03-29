from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse

from .forms import ContactForm
from .models import Partner
from apps.products.models import Product
from apps.services.models import Service
from apps.events.models import Event
from apps.blog.models import Post
from apps.newsletter.models import Subscriber


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["services"]     = Service.objects.filter(
            is_active=True).order_by("order")[:4]
        ctx["products"]     = Product.objects.filter(
            is_active=True)[:6]
        ctx["next_events"]  = Event.objects.filter(
            status="upcoming").order_by("start_date")[:2]
        ctx["latest_posts"] = Post.objects.filter(
            status="published").order_by("-published_at")[:3]
        ctx["partners"]     = Partner.objects.all().order_by(
            "order")
        return ctx


class AboutView(TemplateView):
    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["partners"] = Partner.objects.all().order_by("order")
        return ctx


class ContactView(FormView):
    template_name = "core/contact.html"
    form_class    = ContactForm

    def get_success_url(self):
        from django.urls import reverse
        return reverse("core:contact")

    def _get_client_ip(self, request):
        x_forwarded = request.META.get(
            'HTTP_X_FORWARDED_FOR'
        )
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            ip        = self._get_client_ip(request)
            cache_key = f"contact_limit_{ip}"
            count     = cache.get(cache_key, 0)
            if count >= 3:
                return HttpResponse(
                    "Trop de messages envoyés. "
                    "Veuillez réessayer dans une heure.",
                    status=429,
                    content_type="text/plain"
                )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        import threading

        ip        = self._get_client_ip(self.request)
        cache_key = f"contact_limit_{ip}"
        count     = cache.get(cache_key, 0)
        cache.set(cache_key, count + 1, timeout=3600)

        # Sauvegarde synchrone (rapide)
        form.save()

        # Envoi email en arrière-plan
        def send_async():
            try:
                form.send_email()
            except Exception:
                pass

        t = threading.Thread(target=send_async, daemon=True)
        t.start()

        # Newsletter si cochée
        if self.request.POST.get("subscribe_newsletter"):
            email = form.cleaned_data.get("email")
            if email:
                Subscriber.objects.get_or_create(email=email)

        messages.success(
            self.request,
            "Votre message a bien été envoyé. "
            "Nous vous répondrons dans les plus brefs délais !"
        )
        return super().form_valid(form)

