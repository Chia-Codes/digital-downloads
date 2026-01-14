from django.db import migrations


def noop(*args, **kwargs):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
        ("orders", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(noop, noop),
    ]
