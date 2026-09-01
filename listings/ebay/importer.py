from decimal import Decimal
from datetime import datetime
import re

from django.db import transaction

from listings.models import TempSummary


def clean_text(text: str) -> str:
    """Remove emojis and other non-BMP Unicode characters."""

    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)

    return text.strip()


def extract_images(item):

    urls = []

    image = item.get("image") or {}

    for key in (
        "imageUrl",
        "originalImageUrl",
        "thumbnailImageUrl",
    ):
        if image.get(key):
            urls.append(image[key])

    for key in (
        "additionalImages",
        "thumbnailImages",
    ):
        for img in item.get(key, []):

            if isinstance(img, dict):

                url = img.get("imageUrl")

                if url:
                    urls.append(url)

    for key in (
        "galleryPlusPictureURL",
        "pictureURLLarge",
        "pictureURLSuperSize",
    ):

        if item.get(key):
            urls.append(item[key])

    # remove duplicates while preserving order
    return list(dict.fromkeys(urls))


@transaction.atomic
def save_temp_summaries(items):

    item_ids = [
        item["itemId"]
        for item in items
        if item.get("itemId")
    ]

    existing = set(
        TempSummary.objects.filter(
            ebay_item_id__in=item_ids
        ).values_list(
            "ebay_item_id",
            flat=True,
        )
    )

    new_rows = []

    for item in items:

        item_id = item.get("itemId")

        if not item_id:
            continue

        if item_id in existing:
            continue

        price_info = item.get("price", {})
        price_value = price_info.get("value")

        created = None

        if item.get("itemCreationDate"):

            created = datetime.fromisoformat(
                item["itemCreationDate"].replace(
                    "Z",
                    "+00:00",
                )
            )

        seller = item.get("seller", {})
        location = item.get("itemLocation", {})

        percent = seller.get("feedbackPercentage")

        new_rows.append(

            TempSummary(

                ebay_item_id=item_id,

                title=clean_text(
                    item.get("title", "")
                ),

                price=(
                    Decimal(str(price_value))
                    if price_value
                    else None
                ),

                currency=price_info.get("currency"),

                condition=item.get("condition"),

                buying_options=item.get(
                    "buyingOptions",
                    [],
                ),

                image_urls=extract_images(item),

                item_url=item.get(
                    "itemWebUrl"
                ),

                affiliate_url=item.get(
                    "itemAffiliateWebUrl"
                ),

                seller_username=seller.get(
                    "username"
                ),

                seller_feedback_score=seller.get(
                    "feedbackScore"
                ),

                seller_feedback_percent=(

                    float(
                        percent.replace("%", "")
                    )

                    if percent

                    else None
                ),

                categories=item.get(
                    "categories",
                    [],
                ),

                marketplace=item.get(
                    "marketplace_id"
                ),

                item_country=location.get(
                    "country"
                ),

                item_city=location.get(
                    "city"
                ),

                postal_code=location.get(
                    "postalCode"
                ),

                item_created_at=created,
            )
        )

    TempSummary.objects.bulk_create(
        new_rows,
        batch_size=500,
    )

    print(
        f"Inserted {len(new_rows)} rows into temp_summaries."
    )