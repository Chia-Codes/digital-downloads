import pytest
from django.urls import reverse


# Home page renders correctly
@pytest.mark.django_db
def test_home_page(client):
    resp = client.get(reverse("core:home"))
    assert resp.status_code == 200
    assert b"Digital Downloads" in resp.content
