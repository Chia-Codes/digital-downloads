from __future__ import annotations

from typing import Dict

__all__ = ["add_to_cart", "get_cart", "save_cart", "clear_cart"]

CART_SESSION_KEY = "cart"


# Add to the cart
def add_to_cart(request, product_id, qty: int = 1) -> None:
    cart = request.session.get(CART_SESSION_KEY, {}) or {}
    pid = str(product_id)
    cart[pid] = int(cart.get(pid, 0)) + int(qty)
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


# Get the cart
def get_cart(request) -> Dict[str, int]:
    """Return dict mapping product_id (str) -> quantity (int)."""
    raw = request.session.get(CART_SESSION_KEY, {}) or {}
    # normalize & drop non-positive quantities
    return {str(k): int(v) for k, v in raw.items() if int(v) > 0}


# Save the cart
def save_cart(request, cart: Dict[str, int]) -> None:
    normalized = {str(k): int(v) for k, v in cart.items() if int(v) > 0}
    request.session[CART_SESSION_KEY] = normalized
    request.session.modified = True


# Clear the cart
def clear_cart(request) -> None:
    """Remove the cart from the session completely."""
    request.session.pop(CART_SESSION_KEY, None)
    request.session.modified = True
