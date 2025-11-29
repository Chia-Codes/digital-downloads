import json
from typing import Tuple

from catalog.models import Product
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

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


@require_http_methods(["GET", "POST"])
def add_to_cart(request, product_id: int):
    if request.method == "POST" and request.headers.get("content-type", "").startswith(
        "application/json"
    ):
        payload = json.loads(request.body or "{}")
        qty = int(payload.get("qty", 1))
    else:
        qty = int(request.GET.get("qty") or request.POST.get("qty") or 1)

    # ensure product exists/active
    product = get_object_or_404(Product.objects.only("id"), id=product_id, active=True)

    cart = get_cart(request)
    key = str(product.id)
    cart[key] = int(cart.get(key, 0)) + (qty if qty > 0 else 1)
    save_cart(request, cart)
    # AJAX -> JSON; normal link/form -> redirect to cart
    if request.method == "POST" and request.headers.get("content-type", "").startswith(
        "application/json"
    ):
        items, subtotal = _cart_totals(cart)
        return JsonResponse({"ok": True, "items": items, "subtotal_pennies": subtotal})
    return redirect("cart:view")


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


@require_http_methods(["GET", "POST"])
def remove_from_cart(request, product_id=None):
    # Decide where the id comes from: JSON body or URL param
    ctype = (request.headers.get("content-type") or "").lower()
    if request.method == "POST" and ctype.startswith("application/json"):
        payload = json.loads(request.body or "{}")
        key = str(payload.get("product_id", "")).strip()
    else:
        key = str(product_id or "").strip()

    if not key:
        return JsonResponse({"ok": False, "error": "Missing product_id"}, status=400)

    cart = get_cart(request)
    cart.pop(key, None)
    save_cart(request, cart)

    # If this was an AJAX/JSON call return totals; otherwise redirect to cart
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or ctype.startswith(
        "application/json"
    ):
        items, subtotal = _cart_totals(cart)
        return JsonResponse({"ok": True, "items": items, "subtotal_pennies": subtotal})

    return redirect("cart:view")
