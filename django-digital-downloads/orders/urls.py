from django.urls import path

from .views import download_asset, order_detail, order_history, purchases

app_name = "orders"

urlpatterns = [
    path("", order_history, name="history"),
    path("<uuid:order_id>/", order_detail, name="detail"),
    path("downloads/", purchases, name="downloads"),
    path("download/<uuid:asset_id>/", download_asset, name="download"),
]
