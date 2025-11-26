import pytest
from django.urls import reverse


# Catalog list view
@pytest.mark.django_db
def test_catalog_list_renders(client, product):
    url = reverse("catalog:list")
    resp = client.get(url)
    assert resp.status_code == 200
    assert product.title.encode() in resp.content


# Purchases view requires login
@pytest.mark.django_db
def test_purchases_requires_login(client):
    resp = client.get(reverse("orders:downloads"))
    assert resp.status_code in (302, 401, 403)  # redirect to login


# Purchase view shows owned assets
@pytest.mark.django_db
def test_purchases_lists_owned_assets(client, user, owned_asset):
    client.force_login(user)
    resp = client.get(reverse("orders:downloads"))
    assert resp.status_code == 200
    assert owned_asset.product.title.encode() in resp.content
