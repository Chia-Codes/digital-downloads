from django.urls import path

from .views import start

app_name = "checkout"
urlpatterns = [path("", start, name="start")]
