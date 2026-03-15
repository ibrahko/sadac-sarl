import pytest
from django.urls import reverse
from .models import Service


@pytest.fixture
def service(db):
    return Service.objects.create(
        title="Conseil Agricole",
        short_description="Accompagnement stratégique.",
        description="Description complète du conseil.",
        icon="lightbulb",
        order=1,
        is_active=True,
    )


@pytest.fixture
def inactive_service(db):
    return Service.objects.create(
        title="Service inactif",
        short_description="Masqué.",
        description="Ce service est masqué.",
        order=2,
        is_active=False,
    )


# ===================================================
# TESTS MODÈLE
# ===================================================
@pytest.mark.django_db
class TestServiceModel:

    def test_creation(self, service):
        assert service.title == "Conseil Agricole"
        assert service.is_active is True
        assert service.order == 1
        assert service.icon == "lightbulb"

    def test_slug_auto_generated(self, service):
        assert service.slug == "conseil-agricole"

    def test_str(self, service):
        assert str(service) == "Conseil Agricole"

    def test_inactive_service(self, inactive_service):
        assert inactive_service.is_active is False

    def test_activate_service(self, inactive_service):
        inactive_service.is_active = True
        inactive_service.save()
        updated = Service.objects.get(
            pk=inactive_service.pk
        )
        assert updated.is_active is True

    def test_ordering(self, service, db):
        s2 = Service.objects.create(
            title="Formation",
            short_description="Formation.",
            description="Formation desc.",
            order=2,
            is_active=True,
        )
        services = Service.objects.filter(
            is_active=True
        ).order_by("order")
        assert services[0].title == "Conseil Agricole"
        assert services[1].title == "Formation"

    def test_unique_slug(self, service, db):
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Service.objects.create(
                title="Autre",
                short_description="Autre.",
                description="Autre desc.",
                slug="conseil-agricole",
            )


# ===================================================
# TESTS VUES
# ===================================================
@pytest.mark.django_db
class TestServiceViews:

    def test_list_view_status(self, client, service):
        response = client.get(reverse("services:list"))
        assert response.status_code == 200

    def test_list_view_template(self, client, service):
        response = client.get(reverse("services:list"))
        assert "services/list.html" in [
            t.name for t in response.templates
        ]

    def test_list_contains_service(self, client, service):
        response = client.get(reverse("services:list"))
        assert b"Conseil" in response.content

    def test_inactive_not_in_list(
            self, client, inactive_service):
        response = client.get(reverse("services:list"))
        assert b"Service inactif" not in response.content

    def test_detail_view_status(self, client, service):
        response = client.get(
            reverse("services:detail",
                    kwargs={"slug": service.slug})
        )
        assert response.status_code == 200

    def test_detail_view_template(self, client, service):
        response = client.get(
            reverse("services:detail",
                    kwargs={"slug": service.slug})
        )
        assert "services/detail.html" in [
            t.name for t in response.templates
        ]

    def test_detail_contains_title(self, client, service):
        response = client.get(
            reverse("services:detail",
                    kwargs={"slug": service.slug})
        )
        assert b"Conseil Agricole" in response.content

    def test_detail_404(self, client):
        response = client.get(
            reverse("services:detail",
                    kwargs={"slug": "inexistant"})
        )
        assert response.status_code == 404
