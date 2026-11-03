
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from psycopg.types.json import Jsonb

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

def read_jsonl(filename):
    with open(filename, encoding="utf-8") as file:
        for line in file:
            if line.strip():
                yield json.loads(line)


def import_games(cur):
    print("Importing games...", flush=True)

    count = 0

    for game in read_jsonl("games.jsonl"):
        cur.execute("""
            INSERT INTO games
                (igdb_id, name, slug, raw_data)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (igdb_id) DO UPDATE SET
                name = EXCLUDED.name,
                slug = EXCLUDED.slug,
                raw_data = EXCLUDED.raw_data
        """, (
            game["id"],
            game.get("name"),
            game.get("slug"),
            Jsonb(game)
        ))

        count += 1

        if count % 500 == 0:
            print(f"Imported {count:,} games...", flush=True)

    print(f"Imported {count:,} games in total.")


def import_platforms(cur):
    print("Importing platforms...")

    count = 0

    for platform in read_jsonl("platforms.jsonl"):
        cur.execute("""
            INSERT INTO platforms
                (igdb_id, name, abbreviation, generation,
                 platform_family_id, raw_data)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (igdb_id) DO UPDATE SET
                name = EXCLUDED.name,
                abbreviation = EXCLUDED.abbreviation,
                generation = EXCLUDED.generation,
                platform_family_id = EXCLUDED.platform_family_id,
                raw_data = EXCLUDED.raw_data
        """, (
            platform["id"],
            platform.get("name"),
            platform.get("abbreviation"),
            platform.get("generation"),
            platform.get("platform_family"),
            Jsonb(platform)
        ))

        count += 1

    print(f"Imported {count:,} platforms")


def import_covers(cur):
    print("Importing covers...")

    count = 0
    skipped = 0

    for cover in read_jsonl("covers.jsonl"):
        # skip covers that aren't linked to a game
        if not cover.get("game"):
            skipped += 1
            continue
        
        image_id = cover.get("image_id")

        cur.execute("""
            INSERT INTO covers
                (igdb_id, game_id, image_id, width, height, raw_data)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (igdb_id) DO UPDATE SET
                game_id = EXCLUDED.game_id,
                image_id = EXCLUDED.image_id,
                width = EXCLUDED.width,
                height = EXCLUDED.height,
                raw_data = EXCLUDED.raw_data
        """, (
            cover["id"],
            cover.get("game"),
            image_id,
            cover.get("width"),
            cover.get("height"),
            Jsonb(cover)
        ))

        count += 1

    print(f"Imported {count:,} covers. Skipped {skipped:,} without a game ID.")


def create_game_platforms(cur):
    print("Creating game/platform relationships...")

    cur.execute("DELETE FROM game_platforms")

    cur.execute("""
        INSERT INTO game_platforms (game_id, platform_id)
        SELECT
            g.igdb_id,
            platform_id.value::BIGINT
        FROM games g
        CROSS JOIN LATERAL
            jsonb_array_elements_text(
                COALESCE(g.raw_data->'platforms', '[]'::jsonb)
            ) AS platform_id(value)
        JOIN platforms p
            ON p.igdb_id = platform_id.value::BIGINT
        ON CONFLICT DO NOTHING
    """)

    print(f"Created {cur.rowcount:,} relationships")


def main():
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            import_platforms(cur)
            import_games(cur)
            import_covers(cur)
            create_game_platforms(cur)

    print("IGDB import completed!")


if __name__ == "__main__":
    main()

