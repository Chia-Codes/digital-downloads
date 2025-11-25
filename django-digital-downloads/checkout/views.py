from typing import Any, Dict

import stripe
from cart.utils import get_cart
from catalog.models import Product
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from orders.models import DigitalAsset, Order, OrderItem, UserAsset

# Stripe config
stripe.api_key = settings.STRIPE_SECRET_KEY

# Robust import for Pylance (some stubs don’t expose stripe.error)
try:
    from stripe.error import SignatureVerificationError  # type: ignore

    # [attr-defined]
except Exception:  # pragma: no cover

    class SignatureVerificationError(Exception):
        pass


@login_required
def start(request):
    """
    Create local Order from the current cart and create
    Stripe Checkout Session.
    Redirect user to Stripe-hosted checkout.
    """
    cart: Dict[str, int] = get_cart(request) or {}
    if not cart:
        return redirect("cart:view")

    products = Product.objects.filter(id__in=cart.keys(), active=True)
    if not products:
        return redirect("cart:view")

    order = Order.objects.create(
        user=request.user,
        status="pending",
        currency=settings.STRIPE_CURRENCY,
        subtotal_pennies=0,
        total_pennies=0,
    )

    line_items: list[dict[str, Any]] = []
    subtotal = 0

    for p in products:
        qty = int(cart.get(str(p.id), 1))
        unit_pp = int(p.price_pennies)
        line_total = unit_pp * qty
        subtotal += line_total

        OrderItem.objects.create(
            order=order, product=p, quantity=qty, unit_price_pennies=unit_pp
        )

        line_items.append(
            {
                "quantity": qty,
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY.lower(),
                    "unit_amount": unit_pp,
                    "product_data": {
                        "name": p.title,
                        "metadata": {"product_id": str(p.id), "slug": p.slug},
                    },
                },
            }
        )

    order.subtotal_pennies = subtotal
    order.total_pennies = subtotal
    order.save(update_fields=["subtotal_pennies", "total_pennies"])

    success_url = settings.SITE_BASE_URL + reverse("checkout:success")
    cancel_url = settings.SITE_BASE_URL + reverse("checkout:cancel")

    session = stripe.checkout.Session.create(  # type: ignore[arg-type]
        mode="payment",
        line_items=line_items,
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        metadata={"order_id": str(order.id), "user_id": str(request.user.id)},
    )

    order.stripe_session_id = session.id
    order.save(update_fields=["stripe_session_id"])

    return redirect(session.url)


@login_required
def success(request):
    return render(request, "checkout/success.html")


@login_required
def cancel(request):
    return render(request, "checkout/cancel.html")


@csrf_exempt
def webhook(request):
    """
    Stripe webhook: verify signature; on checkout.session.completed,
    mark order paid and grant UserAsset(s).
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    if not endpoint_secret:
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return HttpResponse(status=400)
    except SignatureVerificationError:
        return HttpResponse(status=400)

    if event.get("type") == "checkout.session.completed":
        session = event.get("data", {}).get("object", {}) or {}
        session_id = session.get("id")
        payment_intent = session.get("payment_intent", "")

        try:
            order = Order.objects.get(stripe_session_id=session_id)
        except Order.DoesNotExist:
            return HttpResponse(status=200)

        if order.status != "paid":
            order.status = "paid"
            order.stripe_payment_intent = payment_intent or ""
            order.save(update_fields=["status", "stripe_payment_intent"])

            items = OrderItem.objects.filter(order=order).select_related("product")
            assets = DigitalAsset.objects.filter(product__in=[i.product for i in items])

            for asset in assets:
                UserAsset.objects.get_or_create(
                    user=order.user, product=asset.product, digital_asset=asset
                )

    return HttpResponse(status=200)
