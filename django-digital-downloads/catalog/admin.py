from django.contrib import admin

from .models import DigitalAsset, Product, UserNote

# Register your models here.


# PRODUCT ADMIN
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price_pennies", "active", "created_at")
    list_filter = ("active",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


# DIGITAL ASSET ADMIN
@admin.register(DigitalAsset)
class DigitalAssetAdmin(admin.ModelAdmin):
    list_display = ("file_name", "product", "size_bytes")


# USER NOTE ADMIN
@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "product", "updated_at")
    search_fields = ("title", "body")
