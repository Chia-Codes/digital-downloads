from django.urls import path

from .views import add_to_cart, cart_view, remove_from_cart, update_quantity

app_name = "cart"

urlpatterns = [
    path("", cart_view, name="view"),
    path("add/<uuid:product_id>/", add_to_cart, name="add"),
    path("update/", update_quantity, name="update"),
    path("remove/<uuid:product_id>/", remove_from_cart, name="remove"),
]
