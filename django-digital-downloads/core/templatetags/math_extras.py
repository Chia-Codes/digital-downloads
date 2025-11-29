from django import template

register = template.Library()


@register.filter
def mul(a, b):
    """
    Multiply two numbers (ints/strings of ints). Returns 0 on bad input.
    Useful for line totals in templates: qty|mul:unit_price_pennies
    """
    try:
        return int(a) * int(b)
    except Exception:
        return 0
