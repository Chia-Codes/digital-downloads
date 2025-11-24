import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.


# PRODUCTS
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=140)
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    price_pennies = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


# DIGITAL ASSETS
class DigitalAsset(models.Model):
    """
    MVP: store file path only; files stored under protected_media
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    file_path = models.CharField(max_length=512)  # path under protected_media/
    file_name = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=64, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)

    def __str__(self) -> str:
        return self.file_name


# USER NOTES
class UserNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=140)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.user} · {self.title}"
