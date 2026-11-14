import os
import re
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'listingforge.settings')
django.setup()
from listings.models import Listing
from canon.models import Platform, TitleCleanupTerm, Game



def load_terms():

    terms = list(
        TitleCleanupTerm.objects.values_list("term", flat=True)
    )

    return terms

def load_platforms():

    platform_data = list (
        Platform.objects.values_list("name", "abbreviation")
    )

    platforms = [name for name, abb in platform_data]
    abbs = [abb for name, abb in platform_data]

    return platforms, abbs

def get_titles():

    titles = Listing.objects.values_list("id", "title") 

    return titles

def words_for_removal(terms, platforms, abbs): 

    # combine all terms, longest first
    words = sorted(
        (term for term in terms + platforms + abbs if term),
        key=len,
        reverse=True
    )

    return words

def clean_title(title, words_to_remove):


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


    # remove punctuation and unnecessary symbols
    title = re.sub(r"[^\w\s]", " ", title)

    # normalise whitespace
    title = re.sub(r"\s+", " ", title).strip()

    title = title.lower()

    return title


def main():

    clean_titles = []

    terms = load_terms()

    platforms, abbs = load_platforms()

    titles = get_titles()

    words_to_remove = words_for_removal(terms, platforms, abbs)

    for id, title in titles: 

        clean = clean_title(title, words_to_remove)

        clean_titles.append((id, clean))

    print(clean_titles)

if __name__ == "__main__":
    main()





