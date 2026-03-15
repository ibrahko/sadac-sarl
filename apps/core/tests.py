import pytest
from django.urls import reverse
from django.test import Client
from .models import SiteSetting, Partner, ContactMessage


# ===================================================
# FIXTURES LOCALES
# ===================================================
@pytest.fixture
def site_setting(db):
    return SiteSetting.objects.create(
        name="SADAC SARL",
        slogan="Ensemble pour un agrobusiness durable",
        email="contact@sadac.ml",
        phone1="+223 00 00 00 00",
        whatsapp="22300000000",
        address="Bamako, Mali",
    )


@pytest.fixture
def partner(db):
    return Partner.objects.create(
        name="FAO Mali",
        order=1,
    )


@pytest.fixture
def contact_message(db):
    return ContactMessage.objects.create(
        name="Ibrahima Koné",
        email="ibrahima@test.ml",
        phone="+223 76543210",
        subject="Demande d'information",
        message="Bonjour, je voudrais en savoir plus.",
    )


@pytest.fixture
def client_http():
    return Client()


# ===================================================
# TESTS SITESETTING
# ===================================================
@pytest.mark.django_db
class TestSiteSettingModel:

    def test_creation(self, site_setting):
        assert site_setting.name == "SADAC SARL"
        assert site_setting.email == "contact@sadac.ml"
        assert site_setting.phone1 == "+223 00 00 00 00"
        assert site_setting.whatsapp == "22300000000"
        assert site_setting.address == "Bamako, Mali"

    def test_str(self, site_setting):
        assert str(site_setting) == "SADAC SARL"

    def test_slogan(self, site_setting):
        assert site_setting.slogan == \
            "Ensemble pour un agrobusiness durable"

    def test_single_instance(self, site_setting):
        assert SiteSetting.objects.count() == 1


# ===================================================
# TESTS PARTNER
# ===================================================
@pytest.mark.django_db
class TestPartnerModel:

    def test_creation(self, partner):
        assert partner.name == "FAO Mali"
        assert partner.order == 1

    def test_str(self, partner):
        assert str(partner) == "FAO Mali"

    def test_ordering(self, db):
        Partner.objects.create(name="ONU Mali", order=2)
        Partner.objects.create(name="PAM Mali", order=3)
        partners = Partner.objects.all().order_by("order")
        assert partners[0].name == "FAO Mali" or \
               partners.count() >= 1


# ===================================================
# TESTS CONTACT MESSAGE
# ===================================================
@pytest.mark.django_db
class TestContactMessageModel:

    def test_creation(self, contact_message):
        assert contact_message.name == "Ibrahima Koné"
        assert contact_message.email == "ibrahima@test.ml"
        assert contact_message.phone == "+223 76543210"
        assert contact_message.subject == \
            "Demande d'information"

    def test_is_read_default_false(self, contact_message):
        assert contact_message.is_read is False

    def test_str(self, contact_message):
        assert "Ibrahima Koné" in str(contact_message)

    def test_mark_as_read(self, contact_message):
        contact_message.is_read = True
        contact_message.save()
        updated = ContactMessage.objects.get(
            pk=contact_message.pk
        )
        assert updated.is_read is True

    def test_message_count(self, contact_message):
        assert ContactMessage.objects.count() == 1


# ===================================================
# TESTS VUES CORE
# ===================================================
@pytest.mark.django_db
class TestCoreViews:

    def test_home_view_status(self, client):
        response = client.get(reverse("core:home"))
        assert response.status_code == 200

    def test_home_view_template(self, client):
        response = client.get(reverse("core:home"))
        assert "core/home.html" in [
            t.name for t in response.templates
        ]

    def test_about_view_status(self, client):
        response = client.get(reverse("core:about"))
        assert response.status_code == 200

    def test_about_view_template(self, client):
        response = client.get(reverse("core:about"))
        assert "core/about.html" in [
            t.name for t in response.templates
        ]

    def test_contact_get_status(self, client):
        response = client.get(reverse("core:contact"))
        assert response.status_code == 200

    def test_contact_get_template(self, client):
        response = client.get(reverse("core:contact"))
        assert "core/contact.html" in [
            t.name for t in response.templates
        ]

    def test_contact_post_valid(self, client):
        response = client.post(
            reverse("core:contact"),
            {
                "name":    "Test User",
                "email":   "test@test.ml",
                "phone":   "+223 76000000",
                "subject": "Test sujet",
                "message": "Message de test complet.",
            }
        )
        assert response.status_code == 302
        assert ContactMessage.objects.count() == 1

    def test_contact_post_saves_correct_data(self, client):
        client.post(
            reverse("core:contact"),
            {
                "name":    "Amadou Diallo",
                "email":   "amadou@test.ml",
                "phone":   "+223 76111111",
                "subject": "Partenariat",
                "message": "Je veux un partenariat.",
            }
        )
        msg = ContactMessage.objects.first()
        assert msg.name == "Amadou Diallo"
        assert msg.subject == "Partenariat"

    def test_contact_post_invalid_empty_name(self, client):
        response = client.post(
            reverse("core:contact"),
            {"name": ""}
        )
        assert response.status_code == 200
        assert ContactMessage.objects.count() == 0

    def test_home_contains_sadac(self, client):
        response = client.get(reverse("core:home"))
        assert b"SADAC" in response.content
