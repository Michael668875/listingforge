import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'listingforge.settings')
django.setup()

from django.db import connection

from canon.models import Platform, TitleCleanupTerm, Game

import re

from canon.models import Platform, TitleCleanupTerm
from listings.models import Listing





def detect_system(title, platform_lookup):

    if not title:
        return None

    title = title.lower()

    for abbreviation, platform_name in platform_lookup:

        pattern = r"(?<!\w)" + re.escape(abbreviation.lower()) + r"(?!\w)"

        if re.search(pattern, title):
            return platform_name

    return None



def load_platform_lookup():

    platforms = Platform.objects.values_list(
        "name", "abbreviation"
    )

    lookup = []

    for name, abbreviation in platforms:

        lookup.append((name, name))

        if abbreviation:
            lookup.append((abbreviation, name))

    # Check longer names first
    lookup.sort(key=lambda x: len(x[0]), reverse=True)

    return lookup


def load_cleanup_data():
    # terms to remove from listing title when comparing to slug
    terms = list(
        TitleCleanupTerm.objects.values_list("term", flat=True)
    )
    # canonical list of platforms to check if they are in the listing title
    platforms = list(
        Platform.objects.values_list("name", flat=True)
    )
    # abbreviated platform names to check for in listing title
    abbs = list(Platform.objects.values_list("abbreviation", flat=True)
    )

    return terms, platforms, abbs



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


def find_best_match(cleaned_title, detected_system):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                g.slug,
                g.igdb_id,
                strict_word_similarity(
                    lower(btrim(replace(g.slug, '-', ' '))),
                    %s
                ) AS score
            FROM games g
            JOIN game_platforms gp
                ON gp.game_id = g.igdb_id
            JOIN platforms p
                ON p.igdb_id = gp.platform_id
            WHERE
                %s %%>> lower(btrim(replace(g.slug, '-', ' ')))
                AND lower(p.name) = lower(%s)
            ORDER BY score DESC, length(g.slug) DESC
            LIMIT 10
        """, [cleaned_title, cleaned_title, detected_system])

        return cursor.fetchall()


#def match_listings():
#
#    terms, platforms, abbs = load_cleanup_data()
#
#    listings = Listing.objects.all()
#
#    for listing in listings:
#
#        cleaned_title = clean_game_title(
#            listing.title,
#            terms,
#            platforms,
#            abbs
#        ).lower().strip()
#
#        matches = find_best_match(cleaned_title)
#
#        print(cleaned_title)
#
#        for slug, igdb_id, score in matches:
#            print(f"{score:.3f} | {slug} | {igdb_id}")




def run_parse():

    terms, platforms, abbs = load_cleanup_data()
    platform_lookup = load_platform_lookup()

    listings = Listing.objects.all()

    total = 0
    matched = 0
    unmatched = 0
    no_platform = 0

    with open("match_results.txt", "w", encoding="utf-8") as f:

        for listing in listings:

            total += 1

            # Detect platform from original listing title
            system = detect_system(
                listing.title,
                platform_lookup
            )

            # Clean title for comparison against IGDB
            cleaned_title = clean_game_title(
                listing.title,
                terms,
                platforms,
                abbs
            ).lower().strip()

            f.write(f"\nOriginal: {listing.title}\n")
            f.write(f"Cleaned:  {cleaned_title}\n")
            f.write(f"Platform: {system}\n")

            if not system:
                no_platform += 1
                f.write("No platform detected\n")
                continue

            # Find matching IGDB games for this platform
            matches = find_best_match(
                cleaned_title,
                system
            )

            if matches:
                matched += 1

                for slug, igdb_id, score in matches:
                    f.write(
                        f"{score:.3f} | {slug} | {igdb_id}\n"
                    )
            else:
                unmatched += 1
                f.write("No matches found\n")

    print(f"Total listings:       {total}")
    print(f"Listings with matches: {matched}")
    print(f"Listings unmatched:   {unmatched}")
    print(f"No platform detected: {no_platform}")


run_parse()
