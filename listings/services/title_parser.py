import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'listingforge.settings')
django.setup()

from rapidfuzz import process, fuzz

from canon.models import Platform, TitleCleanupTerm, Game

import re

from canon.models import Platform, TitleCleanupTerm
from listings.models import Listing

def clean_slugs():
    slugs = Game.objects.values_list("slug", flat=True)

    slug_words = []

    for slug in slugs:
        words = slug.split("-")
        slug_words.append(words)

    return slug_words



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

# replace other function with this:
def load_canonical_games():

    games = Game.objects.values_list(
        "name",
        "platforms__name"
    )

    canonical = {}

    for name, platform in games:

        key = name.lower().strip()

        if key not in canonical:
            canonical[key] = {
                "name": name,
                "platforms": set()
            }

        if platform:
            canonical[key]["platforms"].add(platform.lower())

    return canonical




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

from django.db import connection


def find_best_match(cleaned_title):

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                slug,
                igdb_id,
                strict_word_similarity(
                    lower(btrim(replace(slug, '-', ' '))),
                    %s
                ) AS score

            FROM games

            WHERE %s %%>> lower(btrim(replace(slug, '-', ' ')))

            ORDER BY
                score DESC,
                length(slug) DESC

            LIMIT 5
        """, [cleaned_title, cleaned_title])

        return cursor.fetchall()

# TEST FUNCTION to see if canon game title is in listing title
def match_game(cleaned_title, detected_system, canonical_games):

    if not cleaned_title or not detected_system:
        return None, 0, "unmatched"

    title = cleaned_title.lower().strip()

    # 1. Exact game matching
    if title in canonical_games:

        game = canonical_games[title]

        if detected_system.lower() in game["platforms"]:
            return game["name"], 100, "exact"

        return None, 100, "platform_mismatch"

    # 2. Fuzzy game matching
    result = process.extractOne(
        title,
        canonical_games.keys(),
        scorer=fuzz.ratio
    )

    if result is None:
        return None, 0, "unmatched"

    matched_name, score, _ = result

    game = canonical_games[matched_name]

    # 3. Verify platform
    if detected_system.lower() not in game["platforms"]:
        return None, score, "platform_mismatch"

    # 4. Apply matching thresholds
    if score >= 95:
        return game["name"], score, "fuzzy"

    elif score >= 85:
        return game["name"], score, "review"

    return None, score, "unmatched"


# get game slug and clean it up for comparison with listing title
def load_canon_games():

    games = Game.objects.values_list("slug", "igdb_id")

    canon_games = {}

    for slug, igdb_id in games:
        cleaned_slug = slug.replace("-", " ").lower().strip()
        canon_games[cleaned_slug] = igdb_id

#    test = list(canon_games.items())[:50]
#
#    print(test)

    return canon_games

#load_canon_games()

def match_listings():

    terms, platforms, abbs = load_cleanup_data()

    listings = Listing.objects.all()

    for listing in listings:

        cleaned_title = clean_game_title(
            listing.title,
            terms,
            platforms,
            abbs
        ).lower().strip()

        matches = find_best_match(cleaned_title)

        print(cleaned_title)

        for slug, igdb_id, score in matches:
            print(f"{score:.3f} | {slug} | {igdb_id}")

# compare game slug and listing title
#def match_listings():
#
#    terms, platforms, abbs = load_cleanup_data()
#
#    canon_games = load_canon_games()
#
#    for slug, igdb_id in Game.objects.values_list("slug", "igdb_id"):
#        cleaned_slug = slug.replace("-", " ").lower().strip()
#
#        if cleaned_slug in ["4", "crimson", "revival", "dark", "back", "outright"]:
#            print(slug, igdb_id)
#
#    # TEMPORARY DEBUG
#    print(f"Loaded {len(canon_games)} canonical games")
#
#    listings = Listing.objects.all()
#
#    for listing in listings:
#
#        # Clean eBay listing title
#        cleaned_title = clean_game_title(
#            listing.title,
#            terms,
#            platforms,
#            abbs
#        ).lower().strip()
#
#        best_match = None
#        best_score = 0
#
#        # Compare against every IGDB slug
#        for canon_title, igdb_id in canon_games.items():
#
            
#            match = word_match(cleaned_title, canon_title)
#
#            if match:
#                print(f"MATCH | {cleaned_title} | {canon_title}")
            
#
#            score = fuzz.token_set_ratio(
#                canon_title,
#                cleaned_title
#            )
#
#            if score > best_score:
#                best_score = score
#                best_match = canon_title
#
#        print(
#            f"{best_score:.1f} | {cleaned_title} | {best_match}"
#        )

match_listings()

#def match_listings():
#
#    terms, platforms, abbs = load_cleanup_data()
#
#    canon_games = load_canon_games()
#
#    listings = Listing.objects.all()
#
#    games = []
#
#    count = 0
#
#    for listing in listings:
#
#        cleaned_title = clean_game_title(
#            listing.title,
#            terms,
#            platforms,
#            abbs
#        )
#
#        cleaned_title = cleaned_title.lower().strip()
#
#        best_match = None
#        best_score = 0
#
#        for canon_title, igdb_id in canon_games.items():
#
#            score = fuzz.token_sort_ratio(canon_title, cleaned_title)
#
#            
#
#            print(f"{score} | {canon_title} | {cleaned_title}")

#        if score >= 85:
#            game_id = canon_games.get(cleaned_title)
#
#        if game_id:
#            print(listing.title, "->", game_id)
#
#            games.append(f"{listing.title} | {cleaned_title} -> {game_id}")
#
#            count += 1
#
#    with open("test_listings.txt", "w", encoding="utf-8") as f:
#        f.write("\n".join(games))
#
#    print(count)




# add this to models when ready
#canon_game = models.ForeignKey(
#    "canon.Game",
#    on_delete=models.SET_NULL,
#    null=True,
#    blank=True,
#    related_name="listings"
#)

# use this to display in browser
# {{ listing.canon_game.name }}




def run_parse():

    # Load cleanup data once
    terms, platforms, abbs = load_cleanup_data()

    # Load IGDB games once
    canonical_games = load_canonical_games()

    # Load platforms once
    platform_lookup = load_platform_lookup()



    listings = Listing.objects.all()

    results = []

    exact_count = 0
    fuzzy_count = 0
    review_count = 0
    unmatched_count = 0
    platform_mismatch_count = 0


    for listing in listings:

        # Detect system from original eBay title
        system = detect_system(
            listing.title,
            platform_lookup
        )

        # Clean eBay title
        cleaned_title = clean_game_title(
            listing.title,
            terms,
            platforms,
            abbs
        )

        # Find matching IGDB game
        game, score, method = match_game(
            cleaned_title,
            system,
            canonical_games
        )

        results.append((
            listing.title,
            system or "",
            cleaned_title,
            game if game else "",
            score,
            method
        ))

        # Count results
        if method == "exact":
            exact_count += 1

        elif method == "fuzzy":
            fuzzy_count += 1

        elif method == "review":
            review_count += 1

        elif method == "platform_mismatch":
            platform_mismatch_count += 1

        else:
            unmatched_count += 1

    # Save results
    with open("match_results.txt", "w", encoding="utf-8") as f:

        for original, system, cleaned, matched, score, method in results:

            f.write(
                f"{original} | {system} | {cleaned} | "
                f"{matched} | {score} | {method}\n"
            )

    print(f"Exact matches: {exact_count}")
    print(f"Fuzzy matches: {fuzzy_count}")
    print(f"Needs review: {review_count}")
    print(f"Platform mismatches: {platform_mismatch_count}")
    print(f"Unmatched: {unmatched_count}")


#run_parse()

