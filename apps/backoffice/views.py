from django.views.generic import (
    TemplateView, ListView, CreateView,
    UpdateView, DeleteView, DetailView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone

from apps.products.models import Product, Category
from apps.services.models import Service
from apps.events.models import Event
from apps.media_gallery.models import Gallery, Media
from apps.blog.models import Post
from apps.orders.models import Order
from apps.newsletter.models import Subscriber, Newsletter
from apps.newsletter.services import send_newsletter
from apps.core.models import ContactMessage, Partner, SiteSetting


# ===================================================
# MIXIN SÉCURITÉ : staff uniquement
# ===================================================
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/accounts/login/"

    def test_func(self):
        return self.request.user.is_staff


# ===================================================
# DASHBOARD
# ===================================================
class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = "backoffice/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_products"]    = Product.objects.count()
        ctx["total_services"]    = Service.objects.count()
        ctx["total_events"]      = Event.objects.count()
        ctx["total_posts"]       = Post.objects.count()
        ctx["total_orders"]      = Order.objects.count()
        ctx["new_orders"]        = Order.objects.filter(status="new").count()
        ctx["total_subscribers"] = Subscriber.objects.filter(
                                        is_active=True).count()
        ctx["total_messages"]    = ContactMessage.objects.filter(
                                        is_read=False).count()
        ctx["recent_orders"]     = Order.objects.order_by(
                                        "-created_at")[:5]
        ctx["recent_messages"]   = ContactMessage.objects.order_by(
                                        "-created_at")[:5]
        ctx["upcoming_events"]   = Event.objects.filter(
                                        status="upcoming").order_by(
                                        "start_date")[:3]
        return ctx



# ===================================================
# PRODUITS
# ===================================================
class ProductListView(StaffRequiredMixin, ListView):
    model = Product
    template_name = "backoffice/products/list.html"
    context_object_name = "products"
    paginate_by = 15

    def get_queryset(self):
        return Product.objects.select_related(
            "category").order_by("-created_at")


class ProductCreateView(StaffRequiredMixin, CreateView):
    model = Product
    template_name = "backoffice/products/form.html"
    fields = ["category", "title", "description",
              "image", "price_info", "is_active"]
    success_url = reverse_lazy("backoffice:product_list")

    def form_valid(self, form):
        messages.success(self.request, "Produit créé avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Ajouter un produit"
        ctx["btn_label"] = "Enregistrer"
        return ctx


class ProductUpdateView(StaffRequiredMixin, UpdateView):
    model = Product
    template_name = "backoffice/products/form.html"
    fields = ["category", "title", "description",
              "image", "price_info", "is_active"]
    success_url = reverse_lazy("backoffice:product_list")

    def form_valid(self, form):
        messages.success(self.request, "Produit mis à jour avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Modifier le produit"
        ctx["btn_label"] = "Mettre à jour"
        return ctx


class ProductDeleteView(StaffRequiredMixin, DeleteView):
    model = Product
    template_name = "backoffice/confirm_delete.html"
    success_url = reverse_lazy("backoffice:product_list")

    def form_valid(self, form):
        messages.success(self.request, "Produit supprimé.")
        return super().form_valid(form)


# ===================================================
# CATÉGORIES
# ===================================================
class CategoryListView(StaffRequiredMixin, ListView):
    model = Category
    template_name = "backoffice/products/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    template_name = "backoffice/products/category_form.html"
    fields = ["name", "slug", "description"]
    success_url = reverse_lazy("backoffice:category_list")

    def form_valid(self, form):
        messages.success(self.request, "Catégorie créée avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Ajouter une catégorie"
        return ctx


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    template_name = "backoffice/products/category_form.html"
    fields = ["name", "slug", "description"]
    success_url = reverse_lazy("backoffice:category_list")

    def form_valid(self, form):
        messages.success(self.request, "Catégorie mise à jour.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Modifier la catégorie"
        return ctx


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = "backoffice/confirm_delete.html"
    success_url = reverse_lazy("backoffice:category_list")

    def form_valid(self, form):
        messages.success(self.request, "Catégorie supprimée.")
        return super().form_valid(form)


# ===================================================
# SERVICES
# ===================================================
class ServiceListView(StaffRequiredMixin, ListView):
    model = Service
    template_name = "backoffice/services/list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.order_by("order")


class ServiceCreateView(StaffRequiredMixin, CreateView):
    model = Service
    template_name = "backoffice/services/form.html"
    fields = ["title", "short_description", "description",
              "icon", "image", "order", "is_active"]
    success_url = reverse_lazy("backoffice:service_list")

    def form_valid(self, form):
        messages.success(self.request, "Service créé avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Ajouter un service"
        ctx["btn_label"] = "Enregistrer"
        return ctx


class ServiceUpdateView(StaffRequiredMixin, UpdateView):
    model = Service
    template_name = "backoffice/services/form.html"
    fields = ["title", "short_description", "description",
              "icon", "image", "order", "is_active"]
    success_url = reverse_lazy("backoffice:service_list")

    def form_valid(self, form):
        messages.success(self.request, "Service mis à jour.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Modifier le service"
        ctx["btn_label"] = "Mettre à jour"
        return ctx


class ServiceDeleteView(StaffRequiredMixin, DeleteView):
    model = Service
    template_name = "backoffice/confirm_delete.html"
    success_url = reverse_lazy("backoffice:service_list")

    def form_valid(self, form):
        messages.success(self.request, "Service supprimé.")
        return super().form_valid(form)


# ===================================================
# ÉVÉNEMENTS
# ===================================================
class EventListView(StaffRequiredMixin, ListView):
    model = Event
    template_name = "backoffice/events/list.html"
    context_object_name = "events"
    paginate_by = 15

    def get_queryset(self):
        return Event.objects.order_by("-start_date")


class EventCreateView(StaffRequiredMixin, CreateView):
    model = Event
    template_name = "backoffice/events/form.html"
    fields = ["title", "description", "start_date",
              "end_date", "location", "banner", "status"]
    success_url = reverse_lazy("backoffice:event_list")

    def form_valid(self, form):
        messages.success(self.request, "Événement créé avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Ajouter un événement"
        ctx["btn_label"] = "Enregistrer"
        return ctx


class EventUpdateView(StaffRequiredMixin, UpdateView):
    model = Event
    template_name = "backoffice/events/form.html"
    fields = ["title", "description", "start_date",
              "end_date", "location", "banner", "status"]
    success_url = reverse_lazy("backoffice:event_list")

    def form_valid(self, form):
        messages.success(self.request, "Événement mis à jour.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Modifier l'événement"
        ctx["btn_label"] = "Mettre à jour"
        return ctx


class EventDeleteView(StaffRequiredMixin, DeleteView):
    model = Event
    template_name = "backoffice/confirm_delete.html"
    success_url = reverse_lazy("backoffice:event_list")

    def form_valid(self, form):
        messages.success(self.request, "Événement supprimé.")
        return super().form_valid(form)


# ===================================================
# GALERIE
# ===================================================
class GalleryListView(StaffRequiredMixin, ListView):
    model = Gallery
    template_name = "backoffice/gallery/list.html"
    context_object_name = "galleries"

    def get_queryset(self):
        return Gallery.objects.order_by("-created_at")


class GalleryCreateView(StaffRequiredMixin, CreateView):
    model = Gallery
    template_name = "backoffice/gallery/form.html"
    fields = ["title", "event", "description"]
    success_url = reverse_lazy("backoffice:gallery_list")

    def form_valid(self, form):
        messages.success(self.request, "Galerie créée avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Créer une galerie"
        ctx["btn_label"] = "Enregistrer"
        return ctx


class GalleryUpdateView(StaffRequiredMixin, UpdateView):
    model = Gallery
    template_name = "backoffice/gallery/form.html"
    fields = ["title", "event", "description"]
    success_url = reverse_lazy("backoffice:gallery_list")

    def form_valid(self, form):
        messages.success(self.request, "Galerie mise à jour.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Modifier la galerie"
        ctx["btn_label"] = "Mettre à jour"
        return ctx


class GalleryDeleteView(StaffRequiredMixin, DeleteView):
    model = Gallery
    template_name = "backoffice/confirm_delete.html"
    success_url = reverse_lazy("backoffice:gallery_list")

    def form_valid(self, form):
        messages.success(self.request, "Galerie supprimée.")
        return super().form_valid(form)


# ===================================================
# MÉDIAS
# ===================================================
class MediaCreateView(StaffRequiredMixin, View):
    template_name = "backoffice/gallery/media_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.gallery = get_object_or_404(
            Gallery, pk=kwargs["gallery_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        from django.shortcuts import render
        return render(request, self.template_name, {
            "gallery": self.gallery,
            "form": None,
        })

    def post(self, request, *args, **kwargs):
        media_type = request.POST.get("type", "image")
        caption    = request.POST.get("caption", "")
        order      = request.POST.get("order", 0)

        if media_type == "image":
            # ← Récupère TOUS les fichiers uploadés
            files = request.FILES.getlist("file")
            if not files:
                messages.error(request, "Aucune image sélectionnée.")
                return redirect(
                    "backoffice:media_create",
                    gallery_pk=self.gallery.pk
                )
            count = 0
            for f in files:
                Media.objects.create(
                    gallery=self.gallery,
                    type="image",
                    file=f,
                    caption=caption,
                    order=order,
                )
                count += 1
            messages.success(
                request,
                f"{count} image(s) ajoutée(s) avec succès."
            )

        elif media_type == "video":
            url = request.POST.get("url", "").strip()
            if not url:
                messages.error(request, "URL de vidéo obligatoire.")
                return redirect(
                    "backoffice:media_create",
                    gallery_pk=self.gallery.pk
                )
            Media.objects.create(
                gallery=self.gallery,
                type="video",
                url=url,
                caption=caption,
                order=order,
            )
            messages.success(request, "Vidéo ajoutée avec succès.")

        return redirect(
            "backoffice:gallery_update",
            pk=self.gallery.pk
        )



class MediaDeleteView(StaffRequiredMixin, DeleteView):
    model = Media
    template_name = "backoffice/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "backoffice:gallery_update",
            kwargs={"pk": self.object.gallery.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, "Média supprimé.")
        return super().form_valid(form)


# ===================================================
# BLOG
# ===================================================
class PostListView(StaffRequiredMixin, ListView):
    model = Post
    template_name = "backoffice/blog/list.html"
    context_object_name = "posts"
    paginate_by = 15

    def get_queryset(self):
        return Post.objects.order_by("-created_at")


class PostCreateView(StaffRequiredMixin, CreateView):
    model = Post
    template_name = "backoffice/blog/form.html"
    fields = ["title", "image", "excerpt",
              "content", "status", "published_at"]
    success_url = reverse_lazy("backoffice:post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        if (form.instance.status == "published"
                and not form.instance.published_at):
            form.instance.published_at = timezone.now()
        messages.success(self.request, "Article créé avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Créer un article"
        ctx["btn_label"] = "Publier"
        return ctx


class PostUpdateView(StaffRequiredMixin, UpdateView):
    model = Post
    template_name = "backoffice/blog/form.html"
    fields = ["title", "image", "excerpt",
              "content", "status", "published_at"]
    success_url = reverse_lazy("backoffice:post_list")

    def form_valid(self, form):
        if (form.instance.status == "published"
                and not form.instance.published_at):
            form.instance.published_at = timezone.now()
        messages.success(self.request, "Article mis à jour avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Modifier l'article"
        ctx["btn_label"] = "Mettre à jour"
        return ctx


class PostDeleteView(StaffRequiredMixin, DeleteView):
    model = Post
    template_name = "backoffice/confirm_delete.html"
    success_url = reverse_lazy("backoffice:post_list")

    def form_valid(self, form):
        messages.success(self.request, "Article supprimé.")
        return super().form_valid(form)


# ===================================================
# COMMANDES
# ===================================================
class OrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = "backoffice/orders/list.html"
    context_object_name = "orders"
    paginate_by = 15

    def get_queryset(self):
        qs = Order.objects.select_related("product").order_by("-created_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["current_status"] = self.request.GET.get("status", "")
        ctx["status_choices"] = Order.STATUS_CHOICES
        ctx["count_new"] = Order.objects.filter(status="new").count()
        ctx["count_processing"] = Order.objects.filter(
            status="processing").count()
        ctx["count_delivered"] = Order.objects.filter(
            status="delivered").count()
        return ctx


class OrderDetailView(StaffRequiredMixin, DetailView):
    model = Order
    template_name = "backoffice/orders/detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Order.STATUS_CHOICES
        return ctx


class OrderUpdateStatusView(StaffRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get("status")
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(
                request,
                f"Statut de la commande mis à jour : {order.get_status_display()}"
            )
        else:
            messages.error(request, "Statut invalide.")
        return redirect("backoffice:order_detail", pk=pk)


# ===================================================
# NEWSLETTER
# ===================================================
class SubscriberListView(StaffRequiredMixin, ListView):
    model = Subscriber
    template_name = "backoffice/newsletter/subscribers.html"
    context_object_name = "subscribers"
    paginate_by = 20

    def get_queryset(self):
        qs = Subscriber.objects.order_by("-created_at")
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(email__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_active"]   = Subscriber.objects.filter(
            is_active=True).count()
        ctx["total_inactive"] = Subscriber.objects.filter(
            is_active=False).count()
        ctx["search"] = self.request.GET.get("q", "")
        return ctx


class SendNewsletterView(StaffRequiredMixin, View):
    template_name = "backoffice/newsletter/send.html"

    def get(self, request, *args, **kwargs):
        newsletters       = Newsletter.objects.order_by(
            "-created_at"
        )
        subscribers_count = Subscriber.objects.filter(
            is_active=True
        ).count()
        return render(request, self.template_name, {
            "newsletters":       newsletters,
            "subscribers_count": subscribers_count,
        })

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        if action == "create":
            subject = request.POST.get("subject", "").strip()
            body    = request.POST.get("body", "").strip()
            if subject and body:
                Newsletter.objects.create(
                    subject=subject,
                    body=body,
                    status="draft"
                )
                messages.success(
                    request,
                    "Newsletter créée en brouillon."
                )
            else:
                messages.error(
                    request,
                    "Sujet et contenu obligatoires."
                )

        elif action == "send":
            newsletter_id = request.POST.get("newsletter_id")
            if newsletter_id:
                try:
                    count = send_newsletter(int(newsletter_id))
                    if count > 0:
                        messages.success(
                            request,
                            f"Newsletter en cours d'envoi "
                            f"à {count} abonné(s)."
                        )
                    else:
                        messages.warning(
                            request,
                            "Aucun abonné actif ou newsletter "
                            "déjà envoyée."
                        )
                except Exception as e:
                    messages.error(
                        request,
                        f"Erreur lors de l'envoi : {str(e)}"
                    )
            else:
                messages.error(
                    request,
                    "Aucune newsletter sélectionnée."
                )

        return redirect("backoffice:send_newsletter")


class NewsletterDeleteView(StaffRequiredMixin, DeleteView):
    model = Newsletter
    template_name = "backoffice/confirm_delete.html"
    success_url = reverse_lazy("backoffice:send_newsletter")

    def form_valid(self, form):
        messages.success(self.request, "Newsletter supprimée.")
        return super().form_valid(form)



# ===================================================
# MESSAGES CONTACT
# ===================================================
class ContactMessageListView(StaffRequiredMixin, ListView):
    model = ContactMessage
    template_name = "backoffice/messages/list.html"
    context_object_name = "contact_messages"
    paginate_by = 15

    def get_queryset(self):
        return ContactMessage.objects.order_by("-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["unread_count"] = ContactMessage.objects.filter(
            is_read=False).count()
        return ctx


class ContactMessageDetailView(StaffRequiredMixin, DetailView):
    model = ContactMessage
    template_name = "backoffice/messages/detail.html"
    context_object_name = "message"

    def get(self, request, *args, **kwargs):
        # Marquer comme lu
        obj = self.get_object()
        if not obj.is_read:
            obj.is_read = True
            obj.save()
        return super().get(request, *args, **kwargs)


class ContactMessageDeleteView(StaffRequiredMixin, DeleteView):
    model = ContactMessage
    template_name = "backoffice/confirm_delete.html"
    success_url = reverse_lazy("backoffice:message_list")

    def form_valid(self, form):
        messages.success(self.request, "Message supprimé.")
        return super().form_valid(form)


# ===================================================
# PARTENAIRES
# ===================================================
class PartnerListView(StaffRequiredMixin, ListView):
    model = Partner
    template_name = "backoffice/partners/list.html"
    context_object_name = "partners"

    def get_queryset(self):
        return Partner.objects.order_by("order")


class PartnerCreateView(StaffRequiredMixin, CreateView):
    model = Partner
    template_name = "backoffice/partners/form.html"
    fields = ["name", "logo", "website", "order"]
    success_url = reverse_lazy("backoffice:partner_list")

    def form_valid(self, form):
        messages.success(self.request, "Partenaire ajouté avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Ajouter un partenaire"
        ctx["btn_label"] = "Enregistrer"
        return ctx


class PartnerUpdateView(StaffRequiredMixin, UpdateView):
    model = Partner
    template_name = "backoffice/partners/form.html"
    fields = ["name", "logo", "website", "order"]
    success_url = reverse_lazy("backoffice:partner_list")

    def form_valid(self, form):
        messages.success(self.request, "Partenaire mis à jour.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Modifier le partenaire"
        ctx["btn_label"] = "Mettre à jour"
        return ctx


class PartnerDeleteView(StaffRequiredMixin, DeleteView):
    model = Partner
    template_name = "backoffice/confirm_delete.html"
    success_url = reverse_lazy("backoffice:partner_list")

    def form_valid(self, form):
        messages.success(self.request, "Partenaire supprimé.")
        return super().form_valid(form)


# ===================================================
# PARAMÈTRES DU SITE
# ===================================================
class SiteSettingView(StaffRequiredMixin, View):
    template_name = "backoffice/settings.html"

    def get(self, request, *args, **kwargs):
        setting = SiteSetting.objects.first()
        return render_to_response(
            self.template_name,
            {"setting": setting},
            request
        )

    def post(self, request, *args, **kwargs):
        setting = SiteSetting.objects.first()
        if not setting:
            setting = SiteSetting()

        setting.name        = request.POST.get("name", setting.name)
        setting.slogan      = request.POST.get("slogan", setting.slogan)
        setting.description = request.POST.get("description", setting.description)
        setting.email       = request.POST.get("email", setting.email)
        setting.phone1      = request.POST.get("phone1", setting.phone1)
        setting.phone2      = request.POST.get("phone2", setting.phone2)
        setting.whatsapp    = request.POST.get("whatsapp", setting.whatsapp)
        setting.address     = request.POST.get("address", setting.address)
        setting.facebook_url = request.POST.get(
            "facebook_url", setting.facebook_url)
        setting.youtube_url  = request.POST.get(
            "youtube_url", setting.youtube_url)

        if request.FILES.get("logo"):
            setting.logo = request.FILES["logo"]

        setting.save()
        messages.success(request, "Paramètres mis à jour avec succès.")
        return redirect("backoffice:settings")


# ===================================================
# HELPER
# ===================================================
def render_to_response(template, context, request):
    from django.shortcuts import render
    return render(request, template, context)
