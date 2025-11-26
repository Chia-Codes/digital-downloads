from django.urls import path

from .views import (
    download_asset,
    note_create,
    note_delete,
    note_edit,
    notes_list,
    order_detail,
    order_history,
    purchases,
)

app_name = "orders"

urlpatterns = [
    path("", order_history, name="history"),
    path("<uuid:order_id>/", order_detail, name="detail"),
    path("downloads/", purchases, name="downloads"),
    path("download/<uuid:asset_id>/", download_asset, name="download"),
    path("notes/", notes_list, name="notes_list"),
    path("notes/create/<uuid:product_id>/", note_create, name="note_create"),
    path("notes/<uuid:note_id>/edit/", note_edit, name="note_edit"),
    path("notes/<uuid:note_id>/delete/", note_delete, name="note_delete"),
]
