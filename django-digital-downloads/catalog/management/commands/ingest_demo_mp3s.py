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
    help = "Create Products and DigitalAssets from MP3 files " "under protected_media/."

    def handle(self, *args, **options):
        # models via apps.get_model so this works even during migrations
        Product = apps.get_model("catalog", "Product")
        DigitalAsset = apps.get_model("orders", "DigitalAsset")

        base = Path(settings.BASE_DIR) / "protected_media"
        processed = 0

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

                DigitalAsset.objects.update_or_create(
                    product=p,
                    file_path=f"{sub}/{mp3.name}",
                    defaults={
                        "file_name": mp3.name,
                        "sha256": h,
                        "size_bytes": len(data),
                    },
                )
                processed += 1

        self.stdout.write(self.style.SUCCESS(f"Processed {processed} MP3(s)."))
