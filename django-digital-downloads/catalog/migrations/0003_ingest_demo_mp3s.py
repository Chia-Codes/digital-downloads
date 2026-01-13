import re
import unicodedata
from hashlib import sha256
from pathlib import Path

from django.db import migrations


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower() or "track"


def ingest_demo_mp3s(apps, schema_editor):
    try:
        Product = apps.get_model("catalog", "Product")
        DigitalAsset = apps.get_model("orders", "DigitalAsset")
    except LookupError:
        return
        # No demo files in this environment
        return

    Product = apps.get_model("catalog", "Product")
    DigitalAsset = apps.get_model("orders", "DigitalAsset")

    base = Path(__file__).parent.parent.parent / "protected_media" / "demo"
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
                file_path=f"{sub}/{mp3.name}",  # relative to protected_media/
                defaults={
                    "file_name": mp3.name,
                    "sha256": h,
                    "size_bytes": len(data),
                },
            )
            created += 1

    print(f"[ingest_demo_mp3s] processed {created} mp3(s)")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),  # update to last migration in catalog
        ("orders", "0002_usernote"),  # update to last migration in orders
    ]

    operations = [
        migrations.RunPython(ingest_demo_mp3s, noop),
    ]
