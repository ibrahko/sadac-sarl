from django.urls import path
from .views import ProductOrderView

app_name = "orders"

urlpatterns = [
    path("produit/<slug:slug>/", ProductOrderView.as_view(), name="order_product"),
]
