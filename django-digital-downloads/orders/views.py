import mimetypes
from pathlib import Path

from catalog.models import Product
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UserNoteForm
from .models import Order, OrderItem, UserAsset, UserNote


# User Notes Views
@login_required
def notes_list(request):
    notes = (
        UserNote.objects.filter(user=request.user)
        .select_related("product")
        .order_by("-updated_at")
    )
    return render(request, "orders/notes_list.html", {"notes": notes})


# User Note Create Views
@login_required
def note_create(request, product_id):
    # Only allow creating a note for a product the user owns
    owns = UserAsset.objects.filter(user=request.user, product_id=product_id).exists()
    if not owns:
        messages.error(request, "You can only add notes for products you own.")
        return redirect("orders:notes_list")

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = UserNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.product = product
            note.save()
            messages.success(request, "Note created.")
            return redirect("orders:notes_list")
    else:
        form = UserNoteForm()

    return render(
        request,
        "orders/note_form.html",
        {"form": form, "product": product, "mode": "create"},
    )


# User Note Edit Views
@login_required
def note_edit(request, note_id):
    note = get_object_or_404(UserNote, id=note_id, user=request.user)

    if request.method == "POST":
        form = UserNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated.")
            return redirect("orders:notes_list")
    else:
        form = UserNoteForm(instance=note)

    return render(
        request,
        "orders/note_form.html",
        {"form": form, "product": note.product, "mode": "edit"},
    )


# User Note Delete Views
@login_required
def note_delete(request, note_id):
    note = get_object_or_404(UserNote, id=note_id, user=request.user)

    if request.method == "POST":
        note.delete()
        messages.success(request, "Note deleted.")
        return redirect("orders:notes_list")

    return render(request, "orders/note_confirm_delete.html", {"note": note})


# Orders and Purchases Views
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/history.html", {"orders": orders})


# Order Detail View
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order).select_related("product")
    return render(request, "orders/detail.html", {"order": order, "items": items})


# Purchases View
@login_required
def purchases(request) -> HttpResponse:
    assets = (
        UserAsset.objects.select_related("product", "digital_asset")
        .filter(user=request.user)
        .order_by("-granted_at")
    )
    return render(request, "orders/purchases.html", {"assets": assets})


# Download Asset View
@login_required
def download_asset(request, asset_id) -> FileResponse:
    ua = get_object_or_404(
        UserAsset.objects.select_related("digital_asset", "product"),
        id=asset_id,
        user=request.user,
    )
    # Ensure the file exists
    rel_path = ua.digital_asset.file_path.lstrip("/\\")
    abs_path = Path(settings.BASE_DIR) / "protected_media" / rel_path
    if not abs_path.exists() or not abs_path.is_file():
        raise Http404("File not found")
    # Serve the file as an attachment
    mime, _ = mimetypes.guess_type(abs_path.name)
    response = FileResponse(open(abs_path, "rb"), as_attachment=True)
    if mime:
        response["Content-Type"] = mime
    response["Content-Disposition"] = (
        f'attachment; filename="{ua.digital_asset.file_name}"'
    )
    return response
