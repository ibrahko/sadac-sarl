from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserUpdateForm, UserProfileForm


@method_decorator(login_required, name="dispatch")
class ProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        ctx["profile"] = profile
        return ctx


@method_decorator(login_required, name="dispatch")
class ProfileEditView(TemplateView):
    template_name = "accounts/profile_edit.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user       = self.request.user
        profile, _ = UserProfile.objects.get_or_create(
            user=user
        )
        ctx["user_form"]    = UserUpdateForm(instance=user)
        ctx["profile_form"] = UserProfileForm(
            instance=profile
        )
        return ctx

    def post(self, request, *args, **kwargs):
        user       = request.user
        profile, _ = UserProfile.objects.get_or_create(
            user=user
        )
        user_form    = UserUpdateForm(
            request.POST, instance=user
        )
        profile_form = UserProfileForm(
            request.POST, instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(
                request,
                "Profil mis à jour avec succès."
            )
            return redirect("accounts:profile")  # ← 302

        messages.error(request, "Corrigez les erreurs.")
        return self.render_to_response(
            self.get_context_data()
        )
