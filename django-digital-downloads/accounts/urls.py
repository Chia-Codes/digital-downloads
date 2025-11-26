from django.contrib.auth import views as auth_views
from django.urls import path

from .views import profile, register

app_name = "accounts"

urlpatterns = [
    path(
        "logout/", auth_views.LogoutView.as_view(next_page="core:home"), name="logout"
    ),
    path("register/", register, name="register"),
    path("profile/", profile, name="profile"),
]
