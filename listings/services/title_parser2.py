import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'listingforge.settings')
django.setup()

from django.db import connection

from canon.models import Platform, TitleCleanupTerm, Game

import re

from canon.models import Platform, TitleCleanupTerm
from listings.models import Listing


def load_terms():
    return list(
        TitleCleanupTerm.objects.values_list("term", flat=True)
    )


def load_platforms():

    platform_data = list(
        Platform.objects.values_list("name", "abbreviation")
    )

    platforms = [name for name, abb in platform_data]
    abbs = [abb for name, abb in platform_data]

    return platforms, abbs


def detect_system(title, platforms, abbs):

    if not title:
        return None

    title = title.lower()

    for platform_name, abbreviation in zip(platforms, abbs):

        abbreviation_pattern = r"(?<!\w)" + re.escape(abbreviation.lower()) + r"(?!\w)" if abbreviation else None

        platform_pattern = r"(?<!\w)" + re.escape(platform_name.lower()) + r"(?!\w)"

        if re.search(platform_pattern, title) or (
            abbreviation_pattern and re.search(abbreviation_pattern, title)
        ):
            return platform_name

    return None


# only load canon games that have the detected platform
def load_canon_games(platform_name):

    games = Game.objects.filter(
        platforms__name=platform_name
    ).values_list("slug", "igdb_id")

    return {
        slug.replace("-", " ").lower(): igdb_id
        for slug, igdb_id in games
        if slug
    }


# cache platform entries. e.g. all games for "ps2"
def get_canon_games(platform_name, canon_games):
    
    # check if platform entries have been added to the dictionary. 
    # Add them or skip if already exist.  
    if platform_name not in canon_games: 
        canon_games[platform_name] = load_canon_games(platform_name)

    return canon_games[platform_name]


# clean up listing title for comparison to slug
def clean_game_title(title, terms, platforms, abbs):
    if not title:
        return ""

    # Combine all terms, longest first
    words_to_remove = sorted(
        (term for term in terms + platforms + abbs if term),
        key=len,
        reverse=True
    )

    if words_to_remove:
        pattern = r"(?<!\w)(?:" + "|".join(
            re.escape(word) for word in words_to_remove
        ) + r")(?!\w)"

        title = re.sub(
            pattern,
            " ",
            title,
            flags=re.IGNORECASE
        )

    # Remove punctuation and unnecessary symbols
    title = re.sub(r"[^\w\s]", " ", title)

    # Normalise whitespace
    title = re.sub(r"\s+", " ", title).strip()

    return title


def process_listings(listings, terms, platforms, abbs):

    canon_games = {}
    matched_games = []

    for listing in listings:

        detected_platform = detect_system(
            listing.title,
            platforms,
            abbs
        )

        if not detected_platform:
            continue

        platform_games = get_canon_games(
            detected_platform,
            canon_games
        )

        # Continue cleaning and matching here

        cleaned_title = clean_game_title(
            listing.title,
            terms,
            platforms,
            abbs
        )

#        game_id = platform_games.get(cleaned_title)

#        print("Original:", listing.title)
#        print("Cleaned:", cleaned_title)

        matches = [
            (slug, game_id)
            for slug, game_id in platform_games.items()
            if slug in cleaned_title.lower()
        ]

#        print("Possible matches:", matches[:5])
#        print("---")

        if matches:
            matched_games.append(
                (listing.title, matches)
            )

    return matched_games




def run_parse():

    terms = load_terms()
    platforms, abbs = load_platforms()

    listings = Listing.objects.only("id", "title")

    processed = process_listings(
        listings,
        terms,
        platforms,
        abbs
    )

    with open("test_file.txt", "w", encoding="utf-8") as f:
        for title, game_id in processed:
            f.write(f"{title} | {game_id}\n")


run_parse()

#The responsibilities are now separated
#Function	        Responsibility
#load_terms()	    Load cleanup terms
#load_platforms()	Load platform names and abbreviations
#load_canon_games()	Load canonical games for one platform
#get_canon_games()	Cache canonical games
#detect_system()	Detect platform in listing title
#process_listings()	Process and match listings
#run_parse()	    Coordinate everything

