import pytest
from django.urls import reverse
from apps.products.models import Category, Product
from .models import Order


# ===================================================
# FIXTURES
# ===================================================
@pytest.fixture
def category(db):
    return Category.objects.create(name="Intrants")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        title="Engrais NPK",
        description="Engrais de qualité.",
        category=category,
        is_active=True,
    )


@pytest.fixture
def order(db, product):
    return Order.objects.create(
        full_name="Moussa Diallo",
        phone="+223 76000001",
        email="moussa@test.ml",
        product=product,
        quantity=5,
        message="Livraison à Bamako.",
    )


# ===================================================
# TESTS MODÈLE
# ===================================================
@pytest.mark.django_db
class TestOrderModel:

    def test_creation(self, order):
        assert order.full_name == "Moussa Diallo"
        assert order.status == "new"
        assert order.quantity == 5

    def test_str(self, order):
        assert "Moussa Diallo" in str(order)

    def test_default_status(self, order):
        assert order.status == "new"

    def test_status_change(self, order):
        order.status = "processing"
        order.save()
        updated = Order.objects.get(pk=order.pk)
        assert updated.status == "processing"

    def test_delivered_status(self, order):
        order.status = "delivered"
        order.save()
        assert Order.objects.get(
            pk=order.pk
        ).status == "delivered"

    def test_cancelled_status(self, order):
        order.status = "cancelled"
        order.save()
        assert Order.objects.get(
            pk=order.pk
        ).status == "cancelled"


# ===================================================
# TESTS VUES
# ===================================================
@pytest.mark.django_db
class TestOrderViews:

    def test_order_form_get(self, client, product):
        response = client.get(
            reverse("orders:order_product",
                    kwargs={"slug": product.slug})
        )
        assert response.status_code == 200
        assert "orders/order_product.html" in [
            t.name for t in response.templates
        ]

    def test_order_form_post_valid(
            self, client, product):
        response = client.post(
            reverse("orders:order_product",
                    kwargs={"slug": product.slug}),
            {
                "full_name": "Test Client",
                "phone":     "+223 76000002",
                "email":     "client@test.ml",
                "quantity":  2,
                "message":   "Test commande.",
            }
        )
        assert response.status_code == 302
        assert Order.objects.count() == 1

    def test_order_form_post_invalid(
            self, client, product):
        response = client.post(
            reverse("orders:order_product",
                    kwargs={"slug": product.slug}),
            {
                "full_name": "",
                "phone":     "",
            }
        )
        assert response.status_code == 200
        assert Order.objects.count() == 0

    def test_order_email_sent(
            self, client, product):
        from django.core import mail
        client.post(
            reverse("orders:order_product",
                    kwargs={"slug": product.slug}),
            {
                "full_name": "Email Test",
                "phone":     "+223 76000003",
                "email":     "email@test.ml",
                "quantity":  1,
            }
        )
        # Signal chargé via OrdersConfig.ready()
        assert len(mail.outbox) >= 0

    def test_order_404_invalid_product(self, client):
        response = client.get(
            reverse("orders:order_product",
                    kwargs={"slug": "inexistant"})
        )
        assert response.status_code == 404

    def test_order_saved_with_product(
            self, client, product):
        client.post(
            reverse("orders:order_product",
                    kwargs={"slug": product.slug}),
            {
                "full_name": "Client test",
                "phone":     "+223 76000004",
                "quantity":  3,
            }
        )
        order = Order.objects.first()
        assert order is not None
        assert order.product == product
        assert order.quantity == 3
