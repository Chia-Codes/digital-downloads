import mimetypes
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import UserAsset


@login_required
def purchases(request) -> HttpResponse:
    assets = (
        UserAsset.objects.select_related("product", "digital_asset")
        .filter(user=request.user)
        .order_by("-granted_at")
    )
    return render(request, "orders/purchases.html", {"assets": assets})


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
