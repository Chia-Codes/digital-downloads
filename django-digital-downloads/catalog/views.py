from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Product


# Health Check View
def catalog_health(request):
    qs = Product.objects.all()
    act = Product.objects.filter(active=True)
    return HttpResponse(
        f"total={qs.count()} active={act.count()} slugs={list(act.values_list(
            'slug', flat=True
        ))}"
    )


# Product List View
def product_list(request):
    products = Product.objects.filter(active=True).order_by("-created_at")
    return render(request, "catalog/list.html", {"products": products})


# Product Detail View
def product_detail(request, slug: str):
    product = get_object_or_404(Product, slug=slug, active=True)
    return render(request, "catalog/detail.html", {"product": product})
