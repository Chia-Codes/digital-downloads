from django.shortcuts import redirect, render


def home(request):
    return render(request, "home.html")


def not_found_redirect(request, exception=None):
    return redirect("core:home")


def server_error_redirect(request):
    return redirect("core:home")
