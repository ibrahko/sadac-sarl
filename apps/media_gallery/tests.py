import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.events.models import Event
from .models import Gallery, Media


# ===================================================
# FIXTURES
# ===================================================
@pytest.fixture
def event(db):
    return Event.objects.create(
        title="Événement galerie",
        description="Test galerie.",
        start_date=timezone.now() + timedelta(days=5),
        location="Bamako, Mali",
        status="upcoming",
    )


@pytest.fixture
def past_event(db):
    return Event.objects.create(
        title="Événement passé galerie",
        description="Test passé.",
        start_date=timezone.now() - timedelta(days=5),
        location="Sikasso, Mali",
        status="past",
    )


@pytest.fixture
def gallery(db, event):
    return Gallery.objects.create(
        title="Photos formation",
        event=event,
        description="Album de la formation.",
    )


@pytest.fixture
def gallery_no_event(db):
    return Gallery.objects.create(
        title="Album général",
        description="Sans événement lié.",
    )


@pytest.fixture
def media_video(db, gallery):
    return Media.objects.create(
        gallery=gallery,
        type="video",
        url="https://www.youtube.com/watch?v=test123",
        caption="Vidéo de démonstration",
        order=1,
    )


@pytest.fixture
def media_video_2(db, gallery):
    return Media.objects.create(
        gallery=gallery,
        type="video",
        url="https://www.youtube.com/watch?v=test456",
        caption="Deuxième vidéo",
        order=2,
    )


# ===================================================
# TESTS MODÈLE GALLERY
# ===================================================
@pytest.mark.django_db
class TestGalleryModel:

    def test_creation(self, gallery):
        assert gallery.title == "Photos formation"
        assert gallery.description == \
               "Album de la formation."

    def test_str(self, gallery):
        assert str(gallery) == "Photos formation"

    def test_gallery_with_event(self, gallery, event):
        assert gallery.event == event

    def test_gallery_without_event(self, gallery_no_event):
        assert gallery_no_event.event is None
        assert str(gallery_no_event) == "Album général"

    def test_created_at_auto(self, gallery):
        assert gallery.created_at is not None

    def test_gallery_linked_to_event(
            self, gallery, event):
        assert event.galleries.count() == 1
        assert event.galleries.first() == gallery

    def test_multiple_galleries_per_event(
            self, db, event):
        Gallery.objects.create(
            title="Album 1", event=event
        )
        Gallery.objects.create(
            title="Album 2", event=event
        )
        assert event.galleries.count() == 2

    def test_gallery_ordering(self, db, event):
        g1 = Gallery.objects.create(
            title="Premier album", event=event
        )
        g2 = Gallery.objects.create(
            title="Deuxième album", event=event
        )
        galleries = Gallery.objects.order_by("created_at")
        assert galleries[0] == g1
        assert galleries[1] == g2

    def test_delete_gallery(self, gallery):
        pk = gallery.pk
        gallery.delete()
        assert Gallery.objects.filter(pk=pk).count() == 0


# ===================================================
# TESTS MODÈLE MEDIA
# ===================================================
@pytest.mark.django_db
class TestMediaModel:

    def test_video_creation(self, media_video):
        assert media_video.type == "video"
        assert media_video.url == \
               "https://www.youtube.com/watch?v=test123"
        assert media_video.caption == \
               "Vidéo de démonstration"
        assert media_video.order == 1

    def test_media_str(self, media_video):
        result = str(media_video)
        assert "video" in result
        assert "Photos formation" in result

    def test_media_default_order(self, db, gallery):
        media = Media.objects.create(
            gallery=gallery,
            type="video",
            url="https://youtu.be/abc",
        )
        assert media.order == 0

    def test_media_ordering(
            self, media_video, media_video_2):
        medias = Media.objects.filter(
            gallery=media_video.gallery
        ).order_by("order")
        assert medias[0] == media_video
        assert medias[1] == media_video_2

    def test_media_belongs_to_gallery(
            self, media_video, gallery):
        assert gallery.medias.count() == 1
        assert gallery.medias.first() == media_video

    def test_multiple_medias_per_gallery(
            self, media_video, media_video_2, gallery):
        assert gallery.medias.count() == 2

    def test_delete_gallery_deletes_medias(
            self, gallery, media_video):
        gallery_id = gallery.pk
        gallery.delete()
        assert Media.objects.filter(
            gallery_id=gallery_id
        ).count() == 0

    def test_delete_media(self, media_video):
        pk = media_video.pk
        media_video.delete()
        assert Media.objects.filter(pk=pk).count() == 0

    def test_media_facebook_url(self, db, gallery):
        media = Media.objects.create(
            gallery=gallery,
            type="video",
            url="https://www.facebook.com/watch?v=123",
            caption="Vidéo Facebook",
        )
        assert "facebook" in media.url

    def test_media_youtube_short_url(self, db, gallery):
        media = Media.objects.create(
            gallery=gallery,
            type="video",
            url="https://youtu.be/abcdef",
        )
        assert "youtu.be" in media.url

    def test_media_caption_optional(self, db, gallery):
        media = Media.objects.create(
            gallery=gallery,
            type="video",
            url="https://youtu.be/test",
        )
        assert media.caption == ""

    def test_update_media_caption(self, media_video):
        media_video.caption = "Nouvelle légende"
        media_video.save()
        updated = Media.objects.get(pk=media_video.pk)
        assert updated.caption == "Nouvelle légende"

    def test_update_media_order(self, media_video):
        media_video.order = 5
        media_video.save()
        updated = Media.objects.get(pk=media_video.pk)
        assert updated.order == 5


# ===================================================
# TESTS VUES GALLERY
# ===================================================
@pytest.mark.django_db
class TestGalleryViews:

    def test_list_view_status(self, client, gallery):
        response = client.get(
            reverse("media_gallery:list")
        )
        assert response.status_code == 200

    def test_list_view_template(self, client, gallery):
        response = client.get(
            reverse("media_gallery:list")
        )
        assert "media_gallery/list.html" in [
            t.name for t in response.templates
        ]

    def test_list_contains_gallery(
            self, client, gallery):
        response = client.get(
            reverse("media_gallery:list")
        )
        assert b"Photos formation" in response.content

    def test_list_multiple_galleries(
            self, client, gallery, gallery_no_event):
        response = client.get(
            reverse("media_gallery:list")
        )
        assert b"Photos formation" in response.content
        assert b"Album" in response.content

    def test_empty_gallery_list(self, client):
        response = client.get(
            reverse("media_gallery:list")
        )
        assert response.status_code == 200

    def test_detail_view_status(
            self, client, gallery):
        response = client.get(
            reverse("media_gallery:detail",
                    kwargs={"pk": gallery.pk})
        )
        assert response.status_code == 200

    def test_detail_view_template(
            self, client, gallery):
        response = client.get(
            reverse("media_gallery:detail",
                    kwargs={"pk": gallery.pk})
        )
        assert "media_gallery/album.html" in [
            t.name for t in response.templates
        ]

    def test_detail_contains_title(
            self, client, gallery):
        response = client.get(
            reverse("media_gallery:detail",
                    kwargs={"pk": gallery.pk})
        )
        assert b"Photos formation" in response.content

    def test_detail_contains_media(
            self, client, gallery, media_video):
        response = client.get(
            reverse("media_gallery:detail",
                    kwargs={"pk": gallery.pk})
        )
        assert b"Vid" in response.content

    def test_detail_without_event(
            self, client, gallery_no_event):
        response = client.get(
            reverse("media_gallery:detail",
                    kwargs={"pk": gallery_no_event.pk})
        )
        assert response.status_code == 200
        assert b"Album" in response.content

    def test_detail_404(self, client):
        response = client.get(
            reverse("media_gallery:detail",
                    kwargs={"pk": 99999})
        )
        assert response.status_code == 404

    def test_gallery_with_past_event(
            self, client, db, past_event):
        gallery = Gallery.objects.create(
            title="Photos événement passé",
            event=past_event,
        )
        response = client.get(
            reverse("media_gallery:detail",
                    kwargs={"pk": gallery.pk})
        )
        assert response.status_code == 200
        assert b"Photos" in response.content

    def test_gallery_media_count(
            self, client, gallery,
            media_video, media_video_2):
        assert gallery.medias.count() == 2
        response = client.get(
            reverse("media_gallery:detail",
                    kwargs={"pk": gallery.pk})
        )
        assert response.status_code == 200
