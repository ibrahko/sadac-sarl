import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Event


@pytest.fixture
def upcoming_event(db):
    return Event.objects.create(
        title="Formation maraîchage",
        description="Formation pratique sur le terrain.",
        start_date=timezone.now() + timedelta(days=10),
        location="Bamako, Mali",
        status="upcoming",
    )


@pytest.fixture
def past_event(db):
    return Event.objects.create(
        title="Atelier coopératives",
        description="Atelier de renforcement.",
        start_date=timezone.now() - timedelta(days=5),
        location="Sikasso, Mali",
        status="past",
    )


@pytest.fixture
def cancelled_event(db):
    return Event.objects.create(
        title="Événement annulé",
        description="Annulé.",
        start_date=timezone.now() + timedelta(days=3),
        location="Mopti, Mali",
        status="cancelled",
    )


# ===================================================
# TESTS MODÈLE
# ===================================================
@pytest.mark.django_db
class TestEventModel:

    def test_creation(self, upcoming_event):
        assert upcoming_event.title == "Formation maraîchage"
        assert upcoming_event.status == "upcoming"
        assert upcoming_event.location == "Bamako, Mali"

    def test_slug_auto_generated(self, upcoming_event):
        assert upcoming_event.slug == "formation-maraichage"

    def test_str(self, upcoming_event):
        assert str(upcoming_event) == "Formation maraîchage"

    def test_past_event(self, past_event):
        assert past_event.status == "past"

    def test_cancelled_event(self, cancelled_event):
        assert cancelled_event.status == "cancelled"

    def test_event_with_end_date(self, db):
        event = Event.objects.create(
            title="Salon agricole",
            description="Grand salon.",
            start_date=timezone.now() + timedelta(days=20),
            end_date=timezone.now() + timedelta(days=23),
            location="Bamako, Mali",
            status="upcoming",
        )
        assert event.end_date is not None
        assert event.end_date > event.start_date

    def test_status_change(self, upcoming_event):
        upcoming_event.status = "past"
        upcoming_event.save()
        updated = Event.objects.get(pk=upcoming_event.pk)
        assert updated.status == "past"

    def test_unique_slug(self, upcoming_event, db):
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Event.objects.create(
                title="Doublon",
                description="Doublon.",
                start_date=timezone.now() + timedelta(days=1),
                location="Bamako",
                status="upcoming",
                slug="formation-maraichage",
            )


# ===================================================
# TESTS VUES
# ===================================================
@pytest.mark.django_db
class TestEventViews:

    def test_list_view_status(self, client, upcoming_event):
        response = client.get(reverse("events:list"))
        assert response.status_code == 200

    def test_list_view_template(self, client, upcoming_event):
        response = client.get(reverse("events:list"))
        assert "events/list.html" in [
            t.name for t in response.templates
        ]

    def test_list_contains_event(self, client, upcoming_event):
        response = client.get(reverse("events:list"))
        assert b"Formation" in response.content

    def test_filter_upcoming(self, client, upcoming_event):
        response = client.get(
            reverse("events:list"),
            {"statut": "upcoming"}
        )
        assert response.status_code == 200
        assert b"Formation" in response.content

    def test_filter_past(
            self, client, upcoming_event, past_event):
        response = client.get(
            reverse("events:list"),
            {"statut": "past"}
        )
        assert response.status_code == 200
        assert b"Atelier" in response.content
        assert b"Formation maraichage" \
               not in response.content

    def test_detail_view_status(
            self, client, upcoming_event):
        response = client.get(
            reverse("events:detail",
                    kwargs={"slug": upcoming_event.slug})
        )
        assert response.status_code == 200

    def test_detail_view_template(
            self, client, upcoming_event):
        response = client.get(
            reverse("events:detail",
                    kwargs={"slug": upcoming_event.slug})
        )
        assert "events/detail.html" in [
            t.name for t in response.templates
        ]

    def test_detail_contains_location(
            self, client, upcoming_event):
        response = client.get(
            reverse("events:detail",
                    kwargs={"slug": upcoming_event.slug})
        )
        assert b"Bamako" in response.content

    def test_detail_404(self, client):
        response = client.get(
            reverse("events:detail",
                    kwargs={"slug": "inexistant"})
        )
        assert response.status_code == 404
