import os
import time
from base64 import b64encode

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")
CAMPAIGN_ID = os.getenv("CAMPAIGN_ID")

CATEGORY_ID = "139973"


def get_token():
    """Get an OAuth token from eBay."""

    auth = b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()

    response = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["access_token"]


def fetch_summaries(
    query="game",
    limit=200,
):
    """
    Fetch listings from multiple eBay marketplaces.
    Returns a list of item dictionaries.
    """

    token = get_token()

    marketplaces = {
        "EBAY_US": {"country": "US", "max_items": 100},
        "EBAY_AU": {"country": "AU", "max_items": 100},
        "EBAY_GB": {"country": "GB", "max_items": 100},
        "EBAY_DE": {"country": "DE", "max_items": 100},
    }

    all_items = []

    for market, config in marketplaces.items():

        country_code = config["country"]
        maximum_items = config["max_items"]

        offset = 0
        market_items = []

        while len(market_items) < maximum_items:

            print(f"{market}: page {offset // limit + 1}")

            response = requests.get(
                "https://api.ebay.com/buy/browse/v1/item_summary/search",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-EBAY-C-MARKETPLACE-ID": market,
                    "X-EBAY-C-ENDUSERCTX":
                        f"affiliateCampaignId={CAMPAIGN_ID}",
                },
                params={
                    "q": query,
                    "category_ids": CATEGORY_ID,
                    "limit": limit,
                    "offset": offset,
                    "fieldgroups": "EXTENDED",
                    "filter":
                        f"conditionIds:{{1000|1500|2000|2500|3000}},"
                        f"buyingOptions:{{FIXED_PRICE}},"
                        f"itemLocationCountry:{country_code},"
                        f"Type:{{Mechanical}}",
                },
                timeout=30,
            )

            response.raise_for_status()

            items = response.json().get("itemSummaries", [])

            if not items:
                break

            filtered = []

            for item in items:

                item_country = (
                    item.get("itemLocation", {})
                    .get("country")
                )

                if item_country != country_code:
                    continue

                item["marketplace_id"] = market
                item["marketplace_country"] = (
                    market.split("_", 1)[1]
                )

                filtered.append(item)

            remaining = maximum_items - len(market_items)

            market_items.extend(
                filtered[:remaining]
            )

            offset += limit

            if len(items) < limit:
                break

            time.sleep(0.2)

        print(
            f"{market}: fetched {len(market_items)} items"
        )

        all_items.extend(market_items)

    unique = {
        item["itemId"]: item
        for item in all_items
    }

    print(
        f"Fetched {len(unique)} unique listings."
    )

    return list(unique.values())