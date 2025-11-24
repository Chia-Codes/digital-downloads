from django.urls import path

from .views import order_history

app_name = "orders"

urlpatterns = [
    path("", order_history, name="history"),
]
