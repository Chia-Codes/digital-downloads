import pytest
from catalog.models import Product


# Test Product model creation and active flag
@pytest.mark.django_db
def test_product_create_and_active_flag():
    p = Product.objects.create(
        slug="p1", title="P1", description="D", price_pennies=100, active=True
    )
    assert p.id is not None
    assert p.active is True
