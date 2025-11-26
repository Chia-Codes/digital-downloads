import uuid

from catalog.models import DigitalAsset, Product
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

# Create your models here.


# USER NOTES
class UserNote(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["user", "product"])]

    def __str__(self) -> str:
        return f"{self.user} · {self.product} · {self.title}"


# ORDERS
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    currency = models.CharField(max_length=3, default="GBP")
    subtotal_pennies = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    total_pennies = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    stripe_session_id = models.CharField(max_length=255, blank=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order {self.id} ({self.status})"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price_pennies = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    def line_total(self) -> int:
        return self.quantity * self.unit_price_pennies

    def __str__(self) -> str:
        return f"{self.product} x{self.quantity}"


class UserAsset(models.Model):
    """
    Grants per-user access to a specific DigitalAsset after payment.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assets"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="grants"
    )
    digital_asset = models.ForeignKey(
        DigitalAsset, on_delete=models.CASCADE, related_name="grants"
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "digital_asset")
        ordering = ["-granted_at"]

    def __str__(self) -> str:
        return f"{self.user} → {self.digital_asset.file_name}"
