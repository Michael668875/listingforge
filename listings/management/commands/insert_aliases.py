from django.core.management.base import BaseCommand

from listings.models import Systems, SystemAlias


class Command(BaseCommand):

    def handle(self, *args, **options):

        aliases = {
            "PlayStation": [
                "PS1",
                "PS One",
                "PSone",
                "PSX",
                "Playstation 1",
            ],
            "PlayStation 2": [
                "PS2",
                "Playstation2",
                "PlayStation II",
            ],
            "PlayStation 3": [
                "PS3",
                "Playstation3",
            ],
            "PlayStation 4": [
                "PS4",
                "Playstation4",
            ],
            "PlayStation 5": [
                "PS5",
                "Playstation5",
            ],
            "Xbox": [
                "Original Xbox",
                "Xbox Classic",
            ],
            "Xbox 360": [
                "X360",
                "Xbox360",
            ],
            "Xbox One": [
                "XboxOne",
            ],
            "Xbox Series X": [
                "Series X",
                "Xbox Series X|S",
            ],
            "Xbox Series S": [
                "Series S",
            ],
            "Nintendo Entertainment System": [
                "NES",
                "Nintendo NES",
            ],
            "Super Nintendo": [
                "SNES",
                "Super NES",
                "Super Nintendo Entertainment System",
            ],
            "Nintendo 64": [
                "N64",
                "Nintendo64",
            ],
            "GameCube": [
                "Game Cube",
                "Nintendo GameCube",
            ],
            "Wii": [
                "Nintendo Wii",
            ],
            "Wii U": [
                "WiiU",
                "Nintendo Wii U",
            ],
            "Nintendo Switch": [
                "Switch",
                "Nintendo Switch 1",
            ],
            "Nintendo Switch 2": [
                "Switch 2",
            ],
            "Game Boy": [
                "Gameboy",
                "GB",
                "Nintendo Game Boy",
            ],
            "Game Boy Color": [
                "Gameboy Color",
                "GBC",
            ],
            "Game Boy Advance": [
                "Gameboy Advance",
                "GBA",
            ],
            "Nintendo DS": [
                "DS",
                "NDS",
                "NintendoDS",
            ],
            "Nintendo 3DS": [
                "3DS",
                "Nintendo3DS",
            ],
            "PC": [
                "Windows PC",
                "PC Games",
                "Microsoft Windows",
                "Windows",
            ],
        }

        for system_name, system_aliases in aliases.items():

            system = Systems.objects.get(name=system_name)

            for alias in system_aliases:
                SystemAlias.objects.get_or_create(
                    system=system,
                    alias=alias
                )

        self.stdout.write(
            self.style.SUCCESS("System aliases inserted successfully.")
        )