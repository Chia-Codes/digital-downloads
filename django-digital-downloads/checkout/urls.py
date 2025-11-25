from django.urls import path

from .views import cancel, start, success, webhook

app_name = "checkout"

urlpatterns = [
    path("", start, name="start"),
    path("success/", success, name="success"),
    path("cancel/", cancel, name="cancel"),
    path("webhook/", webhook, name="webhook"),
]
