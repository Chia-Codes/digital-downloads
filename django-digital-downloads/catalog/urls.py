from django.urls import path

from .views import catalog_health, product_detail, product_list

app_name = "catalog"

urlpatterns = [
    path("", product_list, name="list"),
    path("health/", catalog_health, name="health"),
    path("<slug:slug>/", product_detail, name="detail"),
]
