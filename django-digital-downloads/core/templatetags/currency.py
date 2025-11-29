from django import template

register = template.Library()


@register.filter(name="money")
def money(value):
    """
    Format integer pennies (e.g. 299) as '2.99'.
    Safe fallback to 0.00 on bad input.
    """
    try:
        pennies = int(value)
        return f"{pennies / 100:.2f}"
    except Exception:
        return "0.00"
