import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


# ===================================================
# FIXTURES
# ===================================================
@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        password="test1234",
        email="test@sadac.ml",
        first_name="Ibrahima",
        last_name="Koné",
    )


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staffuser",
        password="staff1234",
        email="staff@sadac.ml",
        is_staff=True,
    )


@pytest.fixture
def profile(db, user):
    return UserProfile.objects.create(
        user=user,
        role="editor",
        phone="+223 76000010",
        job_title="Rédacteur web",
    )


@pytest.fixture
def logged_client(client, user):
    client.login(
        username="testuser",
        password="test1234"
    )
    return client


@pytest.fixture
def logged_staff_client(client, staff_user):
    client.login(
        username="staffuser",
        password="staff1234"
    )
    return client


# ===================================================
# TESTS MODÈLE USERPROFILE
# ===================================================
@pytest.mark.django_db
class TestUserProfileModel:

    def test_creation(self, profile):
        assert profile.role == "editor"
        assert profile.phone == "+223 76000010"
        assert profile.job_title == "Rédacteur web"

    def test_str(self, profile):
        result = str(profile)
        assert "testuser" in result or \
               "Ibrahima" in result

    def test_role_display_editor(self, profile):
        assert profile.get_role_display() == "Rédacteur"

    def test_role_admin(self, db, user):
        profile = UserProfile.objects.create(
            user=user,
            role="admin_sadac",
        )
        assert profile.get_role_display() == "Admin SADAC"

    def test_user_relation(self, profile, user):
        assert profile.user == user

    def test_profile_update(self, profile):
        profile.phone = "+223 79999999"
        profile.save()
        updated = UserProfile.objects.get(pk=profile.pk)
        assert updated.phone == "+223 79999999"


# ===================================================
# TESTS LOGIN / LOGOUT
# ===================================================
@pytest.mark.django_db
class TestLoginView:

    def test_login_get(self, client):
        response = client.get(reverse("accounts:login"))
        assert response.status_code == 200

    def test_login_get_template(self, client):
        response = client.get(reverse("accounts:login"))
        assert "accounts/login.html" in [
            t.name for t in response.templates
        ]

    def test_login_valid_credentials(self, client, user):
        response = client.post(
            reverse("accounts:login"),
            {
                "username": "testuser",
                "password": "test1234",
            }
        )
        assert response.status_code == 302

    def test_login_invalid_credentials(self, client, user):
        response = client.post(
            reverse("accounts:login"),
            {
                "username": "testuser",
                "password": "mauvais_mdp",
            }
        )
        assert response.status_code == 200

    def test_login_wrong_username(self, client):
        response = client.post(
            reverse("accounts:login"),
            {
                "username": "inexistant",
                "password": "test1234",
            }
        )
        assert response.status_code == 200

    def test_logout(self, logged_client):
        # Django 6 requiert POST pour logout
        response = logged_client.post(
            reverse("accounts:logout")
        )
        assert response.status_code == 302


# ===================================================
# TESTS VUES PROFIL
# ===================================================
@pytest.mark.django_db
class TestProfileViews:

    def test_profile_requires_login(self, client):
        response = client.get(
            reverse("accounts:profile")
        )
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_profile_authenticated(self, logged_client):
        response = logged_client.get(
            reverse("accounts:profile")
        )
        assert response.status_code == 200

    def test_profile_template(self, logged_client):
        response = logged_client.get(
            reverse("accounts:profile")
        )
        assert "accounts/profile.html" in [
            t.name for t in response.templates
        ]

    def test_profile_contains_username(
            self, logged_client):
        response = logged_client.get(
            reverse("accounts:profile")
        )
        assert b"testuser" in response.content

    def test_profile_edit_requires_login(self, client):
        response = client.get(
            reverse("accounts:profile_edit")
        )
        assert response.status_code == 302

    def test_profile_edit_get(self, logged_client):
        response = logged_client.get(
            reverse("accounts:profile_edit")
        )
        assert response.status_code == 200

    def test_profile_edit_post_valid(
            self, logged_client):
        response = logged_client.post(
            reverse("accounts:profile_edit"),
            {
                "first_name": "Ibrahima",
                "last_name":  "Koné",
                "email":      "nouveau@sadac.ml",
                "phone":      "+223 76111222",
                "job_title":  "Développeur",
                "role":       "editor",
            }
        )
        assert response.status_code == 302
        updated = User.objects.get(username="testuser")
        assert updated.email == "nouveau@sadac.ml"

    def test_staff_can_access_backoffice(
            self, logged_staff_client):
        response = logged_staff_client.get(
            reverse("backoffice:dashboard")
        )
        assert response.status_code == 200

    def test_regular_user_cannot_access_backoffice(
            self, logged_client):
        response = logged_client.get(
            reverse("backoffice:dashboard")
        )
        assert response.status_code in [302, 403]
