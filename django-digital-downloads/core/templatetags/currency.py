from django import template

register = template.Library()


@register.filter
def pennies(value):
    """
    Render integer pennies as 'X.YY' (string).
    Examples:
      299  -> '2.99'
       50  -> '0.50'
        0  -> '0.00'
    """
    try:
        p = int(value)
    except (TypeError, ValueError):
        return "0.00"
    return f"{p // 100}.{p % 100:02d}"
