from django.db import connection

import logging

logger = logging.getLogger(__name__)


def insert_listings():
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO listings (
                ebay_item_id,
                title,
                price,
                currency,
                image_urls,
                condition,
                country,
                affiliate_url,
                last_seen,
                last_updated,
                status,
                miss_count
            )
            SELECT
                ts.ebay_item_id,
                ts.title,
                ts.price,
                ts.currency,
                ts.image_urls,
                ts.condition,
                ts.item_country,
                ts.affiliate_url,
                ts.last_seen,
                NOW(),
                'ACTIVE',
                0
            FROM temp_summaries ts
            WHERE EXISTS (
                SELECT 1
                FROM jsonb_array_elements(ts.categories) AS cat
                WHERE cat->>'categoryId' IN (
                    '139973'
                )
            )
            ON CONFLICT (ebay_item_id)
            DO NOTHING;
        """)
        logger.info("Inserted %s listings.", cursor.rowcount)

def update_listing_prices():
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE listings l
            SET
                price = ts.price,
                last_updated = NOW()
            FROM temp_summaries ts
            WHERE l.ebay_item_id = ts.ebay_item_id
            AND l.status = 'ACTIVE'
            AND l.price <> ts.price;
        """)

        logger.info("Updated %s listing prices.", cursor.rowcount)


def update_seen_listings():
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE listings l
            SET
                status = 'ACTIVE',
                miss_count = 0,
                last_seen = NOW(),
                last_updated = NOW(),
                ended_at = NULL
            FROM temp_summaries ts
            WHERE l.ebay_item_id = ts.ebay_item_id;
        """)

        logger.info("Updated %s seen listings.", cursor.rowcount)


def increment_miss_count():
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE listings l
            SET
                miss_count = COALESCE(miss_count, 0) + 1,
                last_updated = NOW()
            WHERE l.status = 'ACTIVE'
            AND NOT EXISTS (
                SELECT 1
                FROM temp_summaries ts
                WHERE ts.ebay_item_id = l.ebay_item_id
            );
        """)


def mark_ended_listings():
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE listings
            SET
                status = 'ENDED',
                ended_at = NOW(),
                last_updated = NOW()
            WHERE status = 'ACTIVE'
            AND miss_count >= 12;
        """)

        logger.info("Marked %s listings as ended.", cursor.rowcount)


def insert_price_history():
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO price_history (
                listing_id,
                price,
                currency,
                recorded_at
            )
            SELECT
                l.id,
                ts.price,
                ts.currency,
                NOW()
            FROM listings l
            JOIN temp_summaries ts
                ON ts.ebay_item_id = l.ebay_item_id
            LEFT JOIN LATERAL (
                SELECT
                    ph.price,
                    ph.currency
                FROM price_history ph
                WHERE ph.listing_id = l.id
                ORDER BY
                    ph.recorded_at DESC,
                    ph.id DESC
                LIMIT 1
            ) last_ph ON TRUE
            WHERE
                last_ph.price IS NULL
                OR last_ph.price <> ts.price
                OR last_ph.currency <> ts.currency;
        """)

        logger.info(
            "Inserted %s price history rows.", cursor.rowcount
        )


def truncate_temp_summaries():
    with connection.cursor() as cursor:
        cursor.execute("""
            TRUNCATE TABLE temp_summaries;
        """)

        logger.info("Truncated temp_summaries.")


#def pipeline():
#    conn = connect_to_db()
#
#    try:
#        insert_listings(conn)
#        update_listing_prices(conn)
#        update_seen_listings(conn)
#        increment_miss_count(conn)
#        mark_ended_listings(conn)
#        insert_price_history(conn)
#
#        conn.commit()
#
#    except Exception as e:
#        conn.rollback()
#        print(f"An error occurred during insertion: {e}")
#        raise
#
#    finally:
#        if conn is not None:
#            conn.close()
#            print("Database connection closed.")

