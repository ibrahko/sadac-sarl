import pytest
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Post

User = get_user_model()


@pytest.fixture
def author(db):
    return User.objects.create_user(
        username="auteur",
        password="test1234",
        email="auteur@sadac.ml",
    )


@pytest.fixture
def published_post(db, author):
    return Post.objects.create(
        title="Actualité SADAC",
        excerpt="Résumé de l'actualité.",
        content="Contenu complet de l'article.",
        status="published",
        published_at=timezone.now(),
        author=author,
    )


@pytest.fixture
def draft_post(db, author):
    return Post.objects.create(
        title="Brouillon non publié",
        content="Pas encore publié.",
        status="draft",
        author=author,
    )


# ===================================================
# TESTS MODÈLE
# ===================================================
@pytest.mark.django_db
class TestPostModel:

    def test_creation(self, published_post):
        assert published_post.title == "Actualité SADAC"
        assert published_post.status == "published"

    def test_slug_auto_generated(self, published_post):
        assert published_post.slug == "actualite-sadac"

    def test_str(self, published_post):
        assert str(published_post) == "Actualité SADAC"

    def test_draft_post(self, draft_post):
        assert draft_post.status == "draft"

    def test_author_relation(self, published_post, author):
        assert published_post.author == author

    def test_publish_draft(self, draft_post):
        draft_post.status = "published"
        draft_post.published_at = timezone.now()
        draft_post.save()
        updated = Post.objects.get(pk=draft_post.pk)
        assert updated.status == "published"

    def test_unique_slug(self, published_post, db, author):
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Post.objects.create(
                title="Doublon",
                content="Contenu.",
                status="draft",
                author=author,
                slug="actualite-sadac",
            )


# ===================================================
# TESTS VUES
# ===================================================
@pytest.mark.django_db
class TestPostViews:

    def test_list_view_status(
            self, client, published_post):
        response = client.get(reverse("blog:list"))
        assert response.status_code == 200

    def test_list_view_template(
            self, client, published_post):
        response = client.get(reverse("blog:list"))
        assert "blog/list.html" in [
            t.name for t in response.templates
        ]

    def test_list_contains_published(
            self, client, published_post):
        response = client.get(reverse("blog:list"))
        assert b"Actualit" in response.content

    def test_draft_not_in_list(
            self, client, draft_post):
        response = client.get(reverse("blog:list"))
        assert b"Brouillon non publi" \
               not in response.content

    def test_detail_view_status(
            self, client, published_post):
        response = client.get(
            reverse("blog:detail",
                    kwargs={"slug": published_post.slug})
        )
        assert response.status_code == 200

    def test_detail_view_template(
            self, client, published_post):
        response = client.get(
            reverse("blog:detail",
                    kwargs={"slug": published_post.slug})
        )
        assert "blog/detail.html" in [
            t.name for t in response.templates
        ]

    def test_detail_contains_content(
            self, client, published_post):
        response = client.get(
            reverse("blog:detail",
                    kwargs={"slug": published_post.slug})
        )
        assert b"Contenu complet" in response.content

    def test_detail_404(self, client):
        response = client.get(
            reverse("blog:detail",
                    kwargs={"slug": "inexistant"})
        )
        assert response.status_code == 404
