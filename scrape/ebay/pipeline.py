from django.db import transaction

import logging
import time

logger = logging.getLogger(__name__)

from .sql import (
    insert_listings,
    update_listing_prices,
    insert_price_history,
    update_seen_listings,
    increment_miss_count,
    mark_ended_listings,
)


def run_pipeline():
    """
    Synchronise temp_summaries with the permanent tables.
    """

    with transaction.atomic():

        insert_listings()

        update_listing_prices()

        insert_price_history()

        update_seen_listings()

        increment_miss_count()

        mark_ended_listings()

        
