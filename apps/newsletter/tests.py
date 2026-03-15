import pytest
from django.urls import reverse
from django.core import mail
from .models import Subscriber, Newsletter
from .services import send_newsletter


# ===================================================
# FIXTURES
# ===================================================
@pytest.fixture
def subscriber(db):
    return Subscriber.objects.create(
        email="abonne@sadac.ml",
        name="Fatima Traoré",
        is_active=True,
    )


@pytest.fixture
def inactive_subscriber(db):
    return Subscriber.objects.create(
        email="inactif@sadac.ml",
        name="Inactif",
        is_active=False,
    )


@pytest.fixture
def subscriber_two(db):
    return Subscriber.objects.create(
        email="abonne2@sadac.ml",
        name="Moussa Koné",
        is_active=True,
    )


@pytest.fixture
def newsletter_draft(db):
    return Newsletter.objects.create(
        subject="Newsletter Test",
        body="Contenu de la newsletter test.",
        status="draft",
    )


@pytest.fixture
def newsletter_sent(db):
    return Newsletter.objects.create(
        subject="Newsletter Déjà Envoyée",
        body="Contenu déjà envoyé.",
        status="sent",
    )


# ===================================================
# TESTS MODÈLE SUBSCRIBER
# ===================================================
@pytest.mark.django_db
class TestSubscriberModel:

    def test_creation(self, subscriber):
        assert subscriber.email == "abonne@sadac.ml"
        assert subscriber.name == "Fatima Traoré"
        assert subscriber.is_active is True

    def test_str(self, subscriber):
        assert str(subscriber) == "abonne@sadac.ml"

    def test_inactive(self, inactive_subscriber):
        assert inactive_subscriber.is_active is False

    def test_activate_subscriber(
            self, inactive_subscriber):
        inactive_subscriber.is_active = True
        inactive_subscriber.save()
        updated = Subscriber.objects.get(
            pk=inactive_subscriber.pk
        )
        assert updated.is_active is True

    def test_deactivate_subscriber(self, subscriber):
        subscriber.is_active = False
        subscriber.save()
        updated = Subscriber.objects.get(
            pk=subscriber.pk
        )
        assert updated.is_active is False

    def test_unique_email(self, subscriber, db):
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Subscriber.objects.create(
                email="abonne@sadac.ml"
            )

    def test_created_at_auto(self, subscriber):
        assert subscriber.created_at is not None

    def test_count_active(
            self, subscriber, inactive_subscriber):
        count = Subscriber.objects.filter(
            is_active=True
        ).count()
        assert count == 1


# ===================================================
# TESTS MODÈLE NEWSLETTER
# ===================================================
@pytest.mark.django_db
class TestNewsletterModel:

    def test_creation(self, newsletter_draft):
        assert newsletter_draft.subject == \
               "Newsletter Test"
        assert newsletter_draft.status == "draft"
        assert newsletter_draft.body == \
               "Contenu de la newsletter test."

    def test_str(self, newsletter_draft):
        assert str(newsletter_draft) == "Newsletter Test"

    def test_default_status_draft(self, db):
        nl = Newsletter.objects.create(
            subject="Nouveau",
            body="Contenu.",
        )
        assert nl.status == "draft"

    def test_sent_status(self, newsletter_sent):
        assert newsletter_sent.status == "sent"

    def test_created_at_auto(self, newsletter_draft):
        assert newsletter_draft.created_at is not None

    def test_sent_at_null_by_default(
            self, newsletter_draft):
        assert newsletter_draft.sent_at is None


# ===================================================
# TESTS SERVICE D'ENVOI
# ===================================================
@pytest.mark.django_db
class TestSendNewsletterService:

    def test_send_to_active_subscribers(
            self, subscriber, subscriber_two,
            inactive_subscriber, newsletter_draft):
        count = send_newsletter(newsletter_draft.id)
        # Envoyée à 2 actifs seulement
        assert count == 2

    def test_emails_sent_to_outbox(
            self, subscriber, subscriber_two,
            newsletter_draft):
        send_newsletter(newsletter_draft.id)
        assert len(mail.outbox) == 2

    def test_email_subject(
            self, subscriber, newsletter_draft):
        send_newsletter(newsletter_draft.id)
        assert mail.outbox[0].subject == "Newsletter Test"

    def test_newsletter_status_after_send(
            self, subscriber, newsletter_draft):
        send_newsletter(newsletter_draft.id)
        updated = Newsletter.objects.get(
            pk=newsletter_draft.id
        )
        assert updated.status == "sent"

    def test_newsletter_sent_at_set(
            self, subscriber, newsletter_draft):
        send_newsletter(newsletter_draft.id)
        updated = Newsletter.objects.get(
            pk=newsletter_draft.id
        )
        assert updated.sent_at is not None

    def test_newsletter_not_sent_twice(
            self, subscriber, newsletter_draft):
        send_newsletter(newsletter_draft.id)
        count2 = send_newsletter(newsletter_draft.id)
        assert count2 == 0

    def test_no_active_subscribers(
            self, inactive_subscriber,
            newsletter_draft):
        count = send_newsletter(newsletter_draft.id)
        assert count == 0
        assert len(mail.outbox) == 0

    def test_already_sent_newsletter(
            self, subscriber, newsletter_sent):
        count = send_newsletter(newsletter_sent.id)
        assert count == 0


# ===================================================
# TESTS VUE SUBSCRIBE
# ===================================================
@pytest.mark.django_db
class TestSubscribeView:

    def test_subscribe_post_valid(self, client):
        response = client.post(
            reverse("newsletter:subscribe"),
            {
                "email": "nouveau@sadac.ml",
                "name":  "Nouveau Abonné",
            }
        )
        assert response.status_code == 302
        assert Subscriber.objects.filter(
            email="nouveau@sadac.ml"
        ).exists()

    def test_subscribe_creates_active(self, client):
        client.post(
            reverse("newsletter:subscribe"),
            {"email": "actif@sadac.ml"}
        )
        sub = Subscriber.objects.get(
            email="actif@sadac.ml"
        )
        assert sub.is_active is True

    def test_subscribe_duplicate_no_error(
            self, client, subscriber):
        response = client.post(
            reverse("newsletter:subscribe"),
            {"email": "abonne@sadac.ml"}
        )
        assert response.status_code == 302
        # Toujours 1 seul abonné
        assert Subscriber.objects.filter(
            email="abonne@sadac.ml"
        ).count() == 1

    def test_subscribe_redirects(self, client):
        response = client.post(
            reverse("newsletter:subscribe"),
            {"email": "test@sadac.ml"}
        )
        assert response.status_code == 302

    def test_subscribe_empty_email(self, client):
        response = client.post(
            reverse("newsletter:subscribe"),
            {"email": ""}
        )
        # Pas d'abonné créé
        assert Subscriber.objects.count() == 0
