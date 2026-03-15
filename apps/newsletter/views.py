from django.views.generic import View, TemplateView
from django.shortcuts import redirect, render
from .forms import NewsletterSubscribeForm

class SubscribeView(View):
    def post(self, request, *args, **kwargs):
        form = NewsletterSubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            obj, created = form.Meta.model.objects.get_or_create(email=email)
            if created:
                obj.name = form.cleaned_data.get("name", "")
                obj.save()
        return redirect(request.META.get("HTTP_REFERER", "/"))


class SubscribeConfirmView(TemplateView):
    template_name = "newsletter/confirm.html"
