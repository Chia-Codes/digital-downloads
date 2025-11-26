import re
import unicodedata
from hashlib import sha256
from pathlib import Path

from catalog.models import Product
from orders.models import DigitalAsset


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "track"


def ingest_dir(rel_dir: str, price_pennies: int = 299, active: bool = True) -> int:
    base = Path("protected_media") / rel_dir
    if not base.exists():
        print(f"skip: {base} not found")
        return 0
    count = 0
    for mp3 in base.glob("*.mp3"):
        data = mp3.read_bytes()
        h = sha256(data).hexdigest()
        size = len(data)

        title = mp3.stem.replace("_", " ").title()
        slug = slugify(mp3.stem)

        p, _ = Product.objects.get_or_create(
            slug=slug,
            defaults=dict(
                title=title,
                description=f"Royalty-free demo track ({rel_dir})",
                price_pennies=price_pennies,
                active=active,
            ),
        )

        DigitalAsset.objects.update_or_create(
            product=p,
            file_path=f"{rel_dir}/{mp3.name}",  # path relative to protected_media/
            defaults=dict(
                file_name=mp3.name,
                sha256=h,
                size_bytes=size,
            ),
        )
        count += 1
    return count


def main():
    n_products = ingest_dir("products", price_pennies=299, active=True)
    n_samples = ingest_dir(
        "samples", price_pennies=0, active=True
    )  # set to 0 if you want free “samples”
    print(f"Processed {n_products} product MP3(s), {n_samples} sample MP3(s).")


if __name__ == "__main__":
    main()
