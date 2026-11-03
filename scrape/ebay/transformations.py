from django.db import connection, transaction

import logging

logger = logging.getLogger(__name__)

@transaction.atomic
def create_price_drops():
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE lf_price_drops")

        cursor.execute("""
            INSERT INTO lf_price_drops (
                id,
                ebay_item_id,
                title,
                old_price,
                price,
                currency,
                image_urls,
                condition,
                country,
                status,
                affiliate_url,
                last_updated,
                discount_percent
            )
            WITH first_prices AS (
                SELECT
                    listing_id,
                    price AS old_price,
                    ROW_NUMBER() OVER(
                        PARTITION BY listing_id
                        ORDER BY recorded_at, id
                    ) AS rn
                FROM price_history
            ),
            price_drops AS (
                SELECT
                    l.id,
                    l.ebay_item_id,
                    l.title,
                    fp.old_price,
                    l.price,
                    l.currency,
                    l.image_urls,
                    l.condition,
                    l.country,
                    l.status,
                    l.affiliate_url,
                    l.last_updated,
                    (fp.old_price - l.price) * 100.0
                        / fp.old_price AS discount_percent
                FROM listings l
                INNER JOIN first_prices fp
                    ON fp.listing_id = l.id
                    AND fp.rn = 1
                WHERE l.status = 'ACTIVE'
                    AND fp.old_price > l.price
                    AND fp.old_price > 0
            )
            SELECT *
            FROM price_drops
            ORDER BY discount_percent DESC
        """)
        logger.info("Created %s price_drops.", cursor.rowcount)

