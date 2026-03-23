from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from .forms import ContactForm
from apps.products.models import Product
from apps.services.models import Service
from django.contrib import messages
from apps.events.models import Event
from apps.blog.models import Post


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["services"] = Service.objects.filter(is_active=True).order_by("order")[:4]
        ctx["products"] = Product.objects.filter(is_active=True)[:6]
        ctx["next_events"] = Event.objects.filter(status="upcoming").order_by("start_date")[:2]
        ctx["latest_posts"] = Post.objects.filter(status="published").order_by("-published_at")[:3]
        return ctx


class AboutView(TemplateView):
    template_name = "core/about.html"


class ContactView(FormView):
    template_name = "core/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("core:contact")

    def _get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')

    def dispatch(self, request, *args, **kwargs):
        # Rate limit : max 3 soumissions par IP par heure
        if request.method == 'POST':
            ip        = self._get_client_ip(request)
            cache_key = f"contact_limit_{ip}"
            count     = cache.get(cache_key, 0)
            if count >= 3:
                return HttpResponseTooManyRequests(
                    "Trop de messages envoyés. "
                    "Veuillez réessayer dans une heure.",
                    content_type="text/plain"
                )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Incrémenter le compteur IP
        ip        = self._get_client_ip(self.request)
        cache_key = f"contact_limit_{ip}"
        count     = cache.get(cache_key, 0)
        cache.set(cache_key, count + 1, timeout=3600)
        
        form.save()          # crée ContactMessage
        form.send_email()    # mail à SADAC
        # Si la case newsletter est cochée
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
