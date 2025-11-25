from django.urls import path

from .views import add_to_cart, cart_view, remove_from_cart, update_quantity

app_name = "cart"

urlpatterns = [
    path("", cart_view, name="view"),
    path("add/", add_to_cart, name="add"),
    path("update/", update_quantity, name="update"),
    path("remove/", remove_from_cart, name="remove"),
]
