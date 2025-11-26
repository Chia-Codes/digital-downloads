import pytest
from cart.utils import clear_cart, get_cart, save_cart
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test.client import RequestFactory


@pytest.mark.django_db
def test_cart_session_helpers():
    rf = RequestFactory()
    req = rf.get("/")

    # return an HttpResponse
    def _get_response(_request):
        return HttpResponse()

    middleware = SessionMiddleware(_get_response)
    middleware.process_request(req)
    req.session.save()

    assert get_cart(req) == {}
    save_cart(req, {"1": 2})
    assert get_cart(req) == {"1": 2}
    clear_cart(req)
    assert get_cart(req) == {}
