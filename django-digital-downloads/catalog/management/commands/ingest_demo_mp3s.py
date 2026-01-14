import re
import unicodedata
from hashlib import sha256
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower() or "track"


class Command(BaseCommand):
    help = "Seed Products (and DigitalAssets if model exists)"
    "from protected_media/{products,samples}"

    def handle(self, *args, **kwargs):
        Product = apps.get_model("catalog", "Product")
        try:
            DigitalAsset = apps.get_model("orders", "DigitalAsset")
        except LookupError:
            DigitalAsset = None  # still create Products; skip assets

        base = Path(settings.BASE_DIR) / "protected_media"
        created_products = 0
        upserted_assets = 0

        for sub in ("products", "samples"):
            d = base / sub
            if not d.exists():
                continue

            for mp3 in d.glob("*.mp3"):
                data = mp3.read_bytes()
                h = sha256(data).hexdigest()
                slug = slugify(mp3.stem)
                title = mp3.stem.replace("_", " ").title()

                p, _ = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "title": title,
                        "description": "Royalty-free demo track",
                        "price_pennies": 299,
                        "active": True,
                    },
                )
                created_products += int(_)

                if DigitalAsset is not None:
                    DigitalAsset.objects.update_or_create(
                        product=p,
                        file_path=f"{sub}/{mp3.name}",
                        defaults={
                            "file_name": mp3.name,
                            "sha256": h,
                            "size_bytes": len(data),
                        },
                    )
                    upserted_assets += 1

        if DigitalAsset is None:
            self.stdout.write(
                self.style.WARNING(
                    f"[ingest_demo_mp3s] Created/ensured {created_products} "
                    "products. "
                    "Skipped DigitalAsset linking because "
                    "orders.DigitalAsset model "
                    "was not available on this deploy."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"[ingest_demo_mp3s] Created/ensured {created_products} "
                    "products; "
                    f"upserted {upserted_assets} DigitalAsset rows."
                )
            )
