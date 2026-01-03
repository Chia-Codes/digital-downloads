from catalog.models import Product
from django.conf import settings
from django.db import models

# Create your models here.


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(default=5)  # 1–5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # One review per user per product
    class Meta:
        ordering = ("-created_at",)
        unique_together = (("product", "user"),)

    def __str__(self):
        return f"{self.product.title} — {self.user} ({self.rating}/5)"
