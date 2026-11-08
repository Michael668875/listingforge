import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'listingforge.settings')
django.setup()

from rapidfuzz import process, fuzz

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
    terms = list(
        TitleCleanupTerm.objects.values_list("term", flat=True)
    )

    platforms = list(
        Platform.objects.values_list("name", flat=True)
    )

    abbs = list(Platform.objects.values_list("abbreviation", flat=True)
    )

    return terms, platforms, abbs


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



#def match_game(cleaned_title, canonical_games):
#
#    if not cleaned_title:
#        return None, 0, "unmatched"
#
#    title = cleaned_title.lower().strip()
#
#    # 1. Try exact matching first
#    if title in canonical_games:
#
#        return canonical_games[title], 100, "exact"
#
#    # 2. Try fuzzy matching
#    result = process.extractOne(
#        title,
#        canonical_games.keys(),
#        scorer=fuzz.ratio
#    )
#
#    if result is None:
#        return None, 0, "unmatched"
#
#    matched_name, score, _ = result
#
#    # 3. Apply matching thresholds
#    if score >= 95:
#
#        return canonical_games[matched_name], score, "fuzzy"
#
#    elif score >= 85:
#
#        return canonical_games[matched_name], score, "review"
#
#    else:
#
#        return None, score, "unmatched"

#def load_canonical_games():
#
#    games = Game.objects.values_list("name", flat=True)
#
#    canonical = {}
#
#    for name in games:
#        name = name.lower().strip()
#
#        canonical[name] = name
#
#    return canonical

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


run_parse()

#def run_parse():
#    # Load cleanup data once
#    terms, platforms, abbs = load_cleanup_data()
#
#    listings = Listing.objects.values_list("title", flat=True)
#
#    clean = []
#
#    # Process ebay listings
#    for listing in listings:
#
#        cleaned_title = clean_game_title(
#            listing,
#            terms,
#            platforms,
#            abbs
#        )
#
#        clean.append(cleaned_title)
#
#    with open("clean_titles.txt", "w", encoding="utf-8") as f:
#        for clean_title in clean:
#            f.write(clean_title + "\n")
#
#run_parse()


