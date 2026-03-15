import pytest
from django.urls import reverse
from .models import Category, Product


@pytest.fixture
def category(db):
    return Category.objects.create(name="Maraîchage")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        title="Tomates fraîches",
        description="Tomates de qualité supérieure.",
        category=category,
        price_info="5000 FCFA/kg",
        is_active=True,
    )


@pytest.fixture
def inactive_product(db, category):
    return Product.objects.create(
        title="Produit inactif",
        description="Ce produit est masqué.",
        category=category,
        is_active=False,
    )


# ===================================================
# TESTS CATEGORY
# ===================================================
@pytest.mark.django_db
class TestCategoryModel:

    def test_creation(self, category):
        assert category.name == "Maraîchage"

    def test_slug_auto_generated(self, category):
        assert category.slug == "maraichage"

    def test_str(self, category):
        assert str(category) == "Maraîchage"

    def test_unique_slug(self, db):
        from django.db import IntegrityError
        Category.objects.create(
            name="Céréales", slug="cereales"
        )
        with pytest.raises(IntegrityError):
            Category.objects.create(
                name="Autre", slug="cereales"
            )


# ===================================================
# TESTS PRODUCT
# ===================================================
@pytest.mark.django_db
class TestProductModel:

    def test_creation(self, product):
        assert product.title == "Tomates fraîches"
        assert product.is_active is True
        assert product.price_info == "5000 FCFA/kg"

    def test_slug_auto_generated(self, product):
        assert product.slug == "tomates-fraiches"

    def test_str(self, product):
        assert str(product) == "Tomates fraîches"

    def test_category_relation(self, product, category):
        assert product.category == category
        assert category.products.count() == 1

    def test_inactive_product(self, inactive_product):
        assert inactive_product.is_active is False

    def test_activate_product(self, inactive_product):
        inactive_product.is_active = True
        inactive_product.save()
        updated = Product.objects.get(pk=inactive_product.pk)
        assert updated.is_active is True


# ===================================================
# TESTS VUES PRODUCTS
# ===================================================
@pytest.mark.django_db
class TestProductViews:

    def test_list_view_status(self, client, product):
        response = client.get(reverse("products:list"))
        assert response.status_code == 200

    def test_list_view_template(self, client, product):
        response = client.get(reverse("products:list"))
        assert "products/list.html" in [
            t.name for t in response.templates
        ]

    def test_list_contains_product(self, client, product):
        response = client.get(reverse("products:list"))
        assert b"Tomates" in response.content

    def test_inactive_not_in_list(
            self, client, inactive_product):
        response = client.get(reverse("products:list"))
        assert b"Produit inactif" not in response.content

    def test_filter_by_category(
            self, client, product, category):
        response = client.get(
            reverse("products:list"),
            {"categorie": category.slug}
        )
        assert response.status_code == 200
        assert b"Tomates" in response.content

    def test_detail_view_status(self, client, product):
        response = client.get(
            reverse("products:detail",
                    kwargs={"slug": product.slug})
        )
        assert response.status_code == 200

    def test_detail_view_template(self, client, product):
        response = client.get(
            reverse("products:detail",
                    kwargs={"slug": product.slug})
        )
        assert "products/detail.html" in [
            t.name for t in response.templates
        ]

    def test_detail_404(self, client):
        response = client.get(
            reverse("products:detail",
                    kwargs={"slug": "inexistant"})
        )
        assert response.status_code == 404
