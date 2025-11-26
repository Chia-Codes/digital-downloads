import pytest
from catalog.models import Product
from django.contrib.auth.models import User
from orders.models import DigitalAsset, UserAsset


@pytest.fixture
def user(db):
    return User.objects.create_user("alice", password="testpass123")


@pytest.fixture
def product(db):
    return Product.objects.create(
        slug="sample",
        title="Sample Product",
        description="Demo",
        price_pennies=499,
        active=True,
    )


@pytest.fixture
def digital_asset(db, product):
    return DigitalAsset.objects.create(
        product=product,
        file_path="samples/hello.txt",
        file_name="hello.txt",
        sha256="deadbeef",
        size_bytes=5,
    )


@pytest.fixture
def owned_asset(db, user, product, digital_asset):
    return UserAsset.objects.create(
        user=user, product=product, digital_asset=digital_asset
    )
