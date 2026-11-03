import psycopg
import os
from psycopg.types.json import Jsonb

from dotenv import load_dotenv

load_dotenv()

from fetch import fetch_summaries

def connect_to_db():
    print("Connection to the PostgreSQL database...")
    try:
        conn = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        return conn

    except psycopg.Error as e:
        print(f"Database connection failed: {e}")
        raise

def remove_old_data(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            TRUNCATE temp_summaries
        """)
        conn.commit()

        print("Removed old data from temp_summaries.")
    except psycopg.Error as e:
        conn.rollback()
        print(f"Error removing old data: {e}")
        raise


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

    return list(dict.fromkeys(urls))


def insert_records(conn, data):
    print("Inserting ebay data into temp_summaries...")
    try:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO temp_summaries (
                ebay_item_id,
                title,
                price,
                currency,
                condition,
                buying_options,
                image_urls,
                item_url,
                affiliate_url,
                seller_username,
                seller_feedback_score,
                seller_feedback_percent,
                categories,
                marketplace,
                item_country,
                item_city,
                postal_code,
                item_created_at,
                first_seen,
                last_seen,
                last_updated,
                sold_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, 
                NOW(),
                NOW(), 
                NOW(), 
                %s
            )
            ON CONFLICT (ebay_item_id)
            DO UPDATE SET
                title = EXCLUDED.title,
                price = EXCLUDED.price,
                currency = EXCLUDED.currency,
                condition = EXCLUDED.condition,
                buying_options = EXCLUDED.buying_options,
                image_urls = EXCLUDED.image_urls,
                item_url = EXCLUDED.item_url,
                affiliate_url = EXCLUDED.affiliate_url,
                seller_username = EXCLUDED.seller_username,
                seller_feedback_score = EXCLUDED.seller_feedback_score,
                seller_feedback_percent = EXCLUDED.seller_feedback_percent,
                categories = EXCLUDED.categories,
                marketplace = EXCLUDED.marketplace,
                item_country = EXCLUDED.item_country,
                item_city = EXCLUDED.item_city,
                postal_code = EXCLUDED.postal_code,
                item_created_at = EXCLUDED.item_created_at,
                last_seen = NOW(),
                last_updated = NOW(),
                sold_at = EXCLUDED.sold_at
        """, [
            (
                item["itemId"],
                item["title"],
                item["price"]["value"],
                item["price"]["currency"],
                item["condition"],
                Jsonb(item["buyingOptions"]),
                Jsonb(extract_images(item)),
                item["itemWebUrl"],
                item["itemAffiliateWebUrl"],
                item.get("seller", {}).get("username"),
                item.get("seller", {}).get("feedbackScore"),
                item.get("seller", {}).get("feedbackPercentage"), 
                Jsonb(item["categories"]),
                item["marketplace_id"],
                item.get("itemLocation", {}).get("country"),
                item.get("itemLocation", {}).get("city"),
                item.get("itemLocation", {}).get("postalCode"),
                item["itemCreationDate"],
                None,
            )
            for item in data
        ])

        conn.commit()

        print(f"Inserted {len(data)} records.")
    except psycopg.Error as e:
        conn.rollback()
        print(f"Error inserting data into temp_summaries: {e}")
        raise
                

def main():

    conn = None

    try:
        conn = connect_to_db()
        remove_old_data(conn)
        data = fetch_summaries()
        insert_records(conn, data)

    except Exception as e:
        print(f"An error occurred during execution: {e}")
        raise

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")
