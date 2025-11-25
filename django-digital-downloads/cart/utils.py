from typing import Dict

CART_SESSION_KEY = "cart"


def add_to_cart(request, product_id, qty=1):
    cart = request.session.get("cart", {})
    pid = str(product_id)
    cart[pid] = int(cart.get(pid, 0)) + int(qty)
    request.session["cart"] = cart
    request.session.modified = True


def get_cart(request) -> Dict[str, int]:
    """
    Returns dict mapping product_id (str) -> quantity (int).
    """
    return request.session.get(CART_SESSION_KEY, {})


def save_cart(request, cart: Dict[str, int]) -> None:
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True
