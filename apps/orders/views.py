from django.views.generic import FormView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .forms import OrderForm
from .models import Order
from django.contrib import messages
from apps.newsletter.models import Subscriber
from apps.products.models import Product

class ProductOrderView(FormView):
    template_name = "orders/order_product.html"
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(
            Product, slug=kwargs["slug"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["product"] = self.product
        return ctx

    def form_valid(self, form):
        # Sauvegarder la commande
        order = form.save(commit=False)
        order.product  = self.product
        order.save()  # ← déclenche le signal email automatiquement

        # Abonnement newsletter si coché
        if self.request.POST.get("subscribe_newsletter"):
            email = form.cleaned_data.get("email")
            if email:
                Subscriber.objects.get_or_create(
                    email=email,
                    defaults={"name": form.cleaned_data.get("full_name", "")}
                )

        # Message de succès
        messages.success(
            self.request,
            f"Votre demande de commande pour "
            f"« {self.product.title} » a bien été reçue. "
            f"Notre équipe vous contactera très bientôt !"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Veuillez corriger les erreurs dans le formulaire."
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy(
            "products:detail",
            kwargs={"slug": self.product.slug}
        )