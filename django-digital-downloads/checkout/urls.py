from django.urls import path

from .views import checkout_placeholder

app_name = "checkout"

urlpatterns = [
    path("", checkout_placeholder, name="start"),
]
