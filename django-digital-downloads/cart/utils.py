from typing import Dict

CART_SESSION_KEY = "cart"


def get_cart(request) -> Dict[str, int]:
    """
    Returns dict mapping product_id (str) -> quantity (int).
    """
    return request.session.get(CART_SESSION_KEY, {})


def save_cart(request, cart: Dict[str, int]) -> None:
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True
