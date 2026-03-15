import django
import os
import pytest

# ← Configuration Django AVANT tout import de modèle
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'sadac.settings.dev'
)
django.setup()


def pytest_configure(config):
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'sadac.settings.dev'
    )


@pytest.fixture
def client(db):
    from django.test import Client
    return Client()


@pytest.fixture
def admin_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin",
        password="admin1234",
        email="admin@sadac.ml",
    )


@pytest.fixture
def staff_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username="staff",
        password="staff1234",
        email="staff@sadac.ml",
        is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username="user",
        password="user1234",
        email="user@sadac.ml",
    )
