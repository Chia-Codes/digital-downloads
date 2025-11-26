import json

import pytest
from django.test.utils import override_settings
from django.urls import reverse
from orders.models import Order, OrderItem, UserAsset


# Webhook test for marking order as paid and granting assets
@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET="test_secret")
def test_webhook_marks_order_paid_and_grants_assets(
    client, user, product, digital_asset, monkeypatch
):
    # Create pending order and item
    order = Order.objects.create(
        user=user,
        status="pending",
        currency="GBP",
        subtotal_pennies=product.price_pennies,
        total_pennies=product.price_pennies,
        stripe_session_id="cs_test_123",
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        unit_price_pennies=product.price_pennies,
    )

    # Monkeypatch Stripe signature verification to return a fake event
    import stripe

    def fake_construct_event(payload, sig, secret):
        return {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_test_123", "payment_intent": "pi_123"}},
        }

    monkeypatch.setattr(
        stripe.Webhook, "construct_event", staticmethod(fake_construct_event)
    )

    payload = json.dumps({"dummy": True}).encode()
    resp = client.post(
        reverse("checkout:webhook"),
        data=payload,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="sig",
    )
    assert resp.status_code == 200

    order.refresh_from_db()
    assert order.status == "paid"
    assert order.stripe_payment_intent == "pi_123"

    assert UserAsset.objects.filter(user=user, product=product).exists()
