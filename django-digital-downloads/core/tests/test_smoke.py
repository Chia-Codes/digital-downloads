import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_page(client):
    resp = client.get(reverse("core:home"))
    assert resp.status_code == 200
