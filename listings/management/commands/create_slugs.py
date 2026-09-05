from django.core.management.base import BaseCommand
from django.utils.text import slugify

from listings.models import Systems


class Command(BaseCommand):
    help = "Populate slug field for all brands."

    def handle(self, *args, **options):
        used_slugs = set()

        for system in Systems.objects.all():
            slug = slugify(system.name)

            # Ensure uniqueness
            original_slug = slug
            counter = 2
            while slug in used_slugs or Systems.objects.exclude(pk=system.pk).filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            system.slug = slug
            system.save(update_fields=["slug"])
            used_slugs.add(slug)

            self.stdout.write(f"{system.name} -> {slug}")

        self.stdout.write(self.style.SUCCESS("System slugs created successfully."))