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
    help = "Ingest demo MP3s from protected_media/{products,samples}"
    "into Products + DigitalAssets"

    def handle(self, *args, **options):
        # Get models. If orders.DigitalAsset is not ready, exit.
        try:
            Product = apps.get_model("catalog", "Product")
            DigitalAsset = apps.get_model("orders", "DigitalAsset")
        except LookupError:
            self.stdout.write(
                self.style.WARNING(
                    "[ingest_demo_mp3s] Models not ready"
                    "(missing orders.DigitalAsset?). "
                    "Run migrations first and redeploy."
                )
            )
            return

        base = Path(settings.BASE_DIR) / "protected_media"
        if not base.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"[ingest_demo_mp3s] {base} does not exist on this dyno."
                )
            )
            return

        created = 0
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
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"[ingest_demo_mp3s] Processed {created} MP3(s).")
        )
