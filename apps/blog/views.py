from django.views.generic import ListView, DetailView
from .models import Post

class PostListView(ListView):
    model = Post
    template_name = "blog/list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status="published").order_by("-published_at")


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Articles récents sidebar
        ctx["recent_posts"] = Post.objects.filter(
            status="published"
        ).exclude(pk=self.object.pk).order_by("-published_at")[:5]

        # Navigation précédent / suivant
        ctx["previous_post"] = Post.objects.filter(
            status="published",
            published_at__lt=self.object.published_at
        ).order_by("-published_at").first()

        ctx["next_post"] = Post.objects.filter(
            status="published",
            published_at__gt=self.object.published_at
        ).order_by("published_at").first()

        return ctx
