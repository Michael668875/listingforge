from listings.models import SystemAlias, Listing, System

# get the system from the ebay listing title. e.g. "PS2"
def parse_system(title, aliases, game_systems):
    if not title:
        return None
    
    title = title.lower()

    consoles = [game_system for game_system in game_systems if game_system.name.lower() in title]

    if consoles:
        return max(consoles, key=lambda game_system: len(game_system.name))

    candidates = [alias for alias in aliases if alias.alias.lower() in title]

    if candidates:
        return max(candidates, key=lambda alias: len(alias.alias)).system
    
    return None

# add the system to listings
def process_systems():
    aliases = list(SystemAlias.objects.select_related("system"))

    listings = list(Listing.objects.filter(system__isnull=True))

    game_systems = list(System.objects.all())

    for listing in listings:
        listing.system = parse_system(listing.title, aliases, game_systems,)

    listings = [listing for listing in listings if listing.system is not None]

    Listing.objects.bulk_update(
        listings,
        ["system"],
    )

# A one-off function to reprocess all listings to replace wrong system entries
def reprocess_all_systems():
    aliases = list(SystemAlias.objects.select_related("system"))

    listings = list(Listing.objects.all())

    game_systems = list(System.objects.all())

    changed = []

    for listing in listings:
        new_system = parse_system(listing.title, aliases, game_systems,)

        if new_system:
            if (
                listing.system is None
                or len(new_system.name) > len(listing.system.name)
            ):
                listing.system = new_system
                changed.append(listing)

    Listing.objects.bulk_update(
        changed,
        ["system"],
    )
