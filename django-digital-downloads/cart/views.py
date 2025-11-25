import json
from typing import Tuple

from catalog.models import Product
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .utils import get_cart, save_cart


def cart_view(request):
    cart = get_cart(request)
    products = Product.objects.filter(id__in=cart.keys())
    lines = []
    for p in products:
        qty = cart.get(str(p.id), 0)
        lines.append(
            {
                "id": str(p.id),
                "title": p.title,
                "qty": qty,
                "unit_price": p.price_pennies,
                "line_total": qty * p.price_pennies,
                "slug": p.slug,
            }
        )
    items, subtotal = _cart_totals(cart)
    return render(
        request,
        "cart/view.html",
        {"lines": lines, "items": items, "subtotal": subtotal},
    )


def _cart_totals(cart) -> Tuple[int, int]:
    """Returns (items_count, subtotal_pennies)."""
    items = 0
    subtotal = 0
    products = {str(p.id): p for p in Product.objects.filter(id__in=cart.keys())}
    for pid, qty in cart.items():
        p = products.get(pid)
        if not p:
            continue
        items += qty
        subtotal += qty * p.price_pennies
    return items, subtotal


@require_POST
def add_to_cart(request):
    payload = json.loads(request.body or "{}")
    product_id = str(payload.get("product_id"))
    qty = int(payload.get("qty", 1))
    if qty < 1:
        qty = 1

    try:
        Product.objects.only("id").get(id=product_id, active=True)
    except Product.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Invalid product"}, status=400)

    cart = get_cart(request)
    cart[product_id] = cart.get(product_id, 0) + qty
    save_cart(request, cart)
    items, subtotal = _cart_totals(cart)
    return JsonResponse({"ok": True, "items": items, "subtotal_pennies": subtotal})


@require_POST
def update_quantity(request):
    payload = json.loads(request.body or "{}")
    product_id = str(payload.get("product_id"))
    qty = int(payload.get("qty", 1))

    cart = get_cart(request)
    if product_id not in cart:
        return JsonResponse({"ok": False, "error": "Not in cart"}, status=400)

    if qty <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = qty

    save_cart(request, cart)
    items, subtotal = _cart_totals(cart)
    return JsonResponse({"ok": True, "items": items, "subtotal_pennies": subtotal})


@require_POST
def remove_from_cart(request):
    payload = json.loads(request.body or "{}")
    product_id = str(payload.get("product_id"))

    cart = get_cart(request)
    cart.pop(product_id, None)
    save_cart(request, cart)
    items, subtotal = _cart_totals(cart)
    return JsonResponse({"ok": True, "items": items, "subtotal_pennies": subtotal})
