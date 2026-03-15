from django.urls import path
from . import views

app_name = "backoffice"

urlpatterns = [

    # ===== DASHBOARD =====
    path("", views.DashboardView.as_view(), name="dashboard"),

    # ===== PRODUITS =====
    path("produits/",
         views.ProductListView.as_view(), name="product_list"),
    path("produits/ajouter/",
         views.ProductCreateView.as_view(), name="product_create"),
    path("produits/<int:pk>/modifier/",
         views.ProductUpdateView.as_view(), name="product_update"),
    path("produits/<int:pk>/supprimer/",
         views.ProductDeleteView.as_view(), name="product_delete"),

    # ===== CATÉGORIES PRODUITS =====
    path("categories/",
         views.CategoryListView.as_view(), name="category_list"),
    path("categories/ajouter/",
         views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/modifier/",
         views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/supprimer/",
         views.CategoryDeleteView.as_view(), name="category_delete"),

    # ===== SERVICES =====
    path("services/",
         views.ServiceListView.as_view(), name="service_list"),
    path("services/ajouter/",
         views.ServiceCreateView.as_view(), name="service_create"),
    path("services/<int:pk>/modifier/",
         views.ServiceUpdateView.as_view(), name="service_update"),
    path("services/<int:pk>/supprimer/",
         views.ServiceDeleteView.as_view(), name="service_delete"),

    # ===== ÉVÉNEMENTS =====
    path("evenements/",
         views.EventListView.as_view(), name="event_list"),
    path("evenements/ajouter/",
         views.EventCreateView.as_view(), name="event_create"),
    path("evenements/<int:pk>/modifier/",
         views.EventUpdateView.as_view(), name="event_update"),
    path("evenements/<int:pk>/supprimer/",
         views.EventDeleteView.as_view(), name="event_delete"),

    # ===== GALERIE =====
    path("galerie/",
         views.GalleryListView.as_view(), name="gallery_list"),
    path("galerie/ajouter/",
         views.GalleryCreateView.as_view(), name="gallery_create"),
    path("galerie/<int:pk>/modifier/",
         views.GalleryUpdateView.as_view(), name="gallery_update"),
    path("galerie/<int:pk>/supprimer/",
         views.GalleryDeleteView.as_view(), name="gallery_delete"),

    # ===== MÉDIAS =====
    path("galerie/<int:gallery_pk>/medias/ajouter/",
         views.MediaCreateView.as_view(), name="media_create"),
    path("medias/<int:pk>/supprimer/",
         views.MediaDeleteView.as_view(), name="media_delete"),

    # ===== BLOG / ARTICLES =====
    path("articles/",
         views.PostListView.as_view(), name="post_list"),
    path("articles/ajouter/",
         views.PostCreateView.as_view(), name="post_create"),
    path("articles/<int:pk>/modifier/",
         views.PostUpdateView.as_view(), name="post_update"),
    path("articles/<int:pk>/supprimer/",
         views.PostDeleteView.as_view(), name="post_delete"),

    # ===== COMMANDES =====
    path("commandes/",
         views.OrderListView.as_view(), name="order_list"),
    path("commandes/<int:pk>/",
         views.OrderDetailView.as_view(), name="order_detail"),
    path("commandes/<int:pk>/statut/",
         views.OrderUpdateStatusView.as_view(), name="order_update_status"),

    # ===== NEWSLETTER =====
    path("newsletter/abonnes/",
         views.SubscriberListView.as_view(), name="subscriber_list"),
    path("newsletter/envoyer/",
         views.SendNewsletterView.as_view(), name="send_newsletter"),
    path("newsletter/<int:pk>/supprimer/",
         views.NewsletterDeleteView.as_view(), name="newsletter_delete"),

    # ===== MESSAGES CONTACT =====
    path("messages/",
         views.ContactMessageListView.as_view(), name="message_list"),
    path("messages/<int:pk>/",
         views.ContactMessageDetailView.as_view(), name="message_detail"),
    path("messages/<int:pk>/supprimer/",
         views.ContactMessageDeleteView.as_view(), name="message_delete"),

    # ===== PARTENAIRES =====
    path("partenaires/",
         views.PartnerListView.as_view(), name="partner_list"),
    path("partenaires/ajouter/",
         views.PartnerCreateView.as_view(), name="partner_create"),
    path("partenaires/<int:pk>/modifier/",
         views.PartnerUpdateView.as_view(), name="partner_update"),
    path("partenaires/<int:pk>/supprimer/",
         views.PartnerDeleteView.as_view(), name="partner_delete"),

    # ===== PARAMÈTRES SITE =====
    path("parametres/",
         views.SiteSettingView.as_view(), name="settings"),
]
