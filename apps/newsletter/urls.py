from django.urls import path
from .views import SubscribeView, SubscribeConfirmView

app_name = "newsletter"

urlpatterns = [
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("merci/", SubscribeConfirmView.as_view(), name="confirm"),
]
