from catalog.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from .models import Review

# Create your views here.


@login_required
def add_review(request, slug):
    if request.method != "POST":
        return redirect("catalog:detail", slug=slug)

    product = get_object_or_404(Product, slug=slug, active=True)
    rating = int(request.POST.get("rating") or 5)
    comment = (request.POST.get("comment") or "").strip()

    # Enforce 1 review per user per product (per model Meta)
    Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={"rating": rating, "comment": comment},
    )
    messages.success(request, "Thanks for your review!")
    return redirect("catalog:detail", slug=slug)
