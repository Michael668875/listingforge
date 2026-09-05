from django.core.management.base import BaseCommand

from listings.models import Systems

class Command(BaseCommand):



    def handle(self, *args, **options):

        systems = [
            "PlayStation",
            "PlayStation 2",
            "PlayStation 3",
            "PlayStation 4",
            "PlayStation 5",
            "Xbox",
            "Xbox 360",
            "Xbox One",
            "Xbox Series X",
            "Xbox Series S",
            "Nintendo Entertainment System",
            "Super Nintendo",
            "Nintendo 64",
            "GameCube",
            "Wii",
            "Wii U",
            "Nintendo Switch",
            "Nintendo Switch 2",
            "Game Boy",
            "Game Boy Color",
            "Game Boy Advance",
            "Nintendo DS",
            "Nintendo 3DS",
            "PC",
        ]


        for name in systems:
            Systems.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS("Systems inserted successfully."))
