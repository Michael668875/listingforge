import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'listingforge.settings')
django.setup()

from canon.models import Platform, TitleCleanupTerm

import re

from canon.models import Platform, TitleCleanupTerm
from listings.models import Listing


def load_cleanup_data():
    terms = list(
        TitleCleanupTerm.objects.values_list("term", flat=True)
    )

    platforms = list(
        Platform.objects.values_list("name", flat=True)
    )

    return terms, platforms


def clean_game_title(title, terms, platforms):
    if not title:
        return ""


    # Combine all terms, longest first
    words_to_remove = sorted(
        terms + platforms,
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



def run_parse():
    # Load cleanup data once
    terms, platforms = load_cleanup_data()

    listings = Listing.objects.all()

    clean = []

    # Process ebay listings
    for listing in listings:

        cleaned_title = clean_game_title(
            listing.title,
            terms,
            platforms
        )

        clean.append(cleaned_title)

    with open("clean_titles.txt", "w", encoding="utf-8") as f:
        for clean_title in clean:
            f.write(clean_title + "\n")

run_parse()


