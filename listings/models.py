from django.db import models
from django.utils import timezone


CURRENCY_SYMBOLS = {
    "USD": "$",
    "AUD": "$",
    "GBP": "£",
    "EUR": "€",
}

# Create your models here.

class TempSummary(models.Model):
    ebay_item_id = models.CharField(max_length=255, unique=True)

    title = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10)

    condition = models.CharField(max_length=255, blank=True, null=True)
    buying_options = models.JSONField(blank=True, null=True)

    image_urls = models.JSONField(blank=True, null=True)

    item_url = models.TextField(blank=True, null=True)
    affiliate_url = models.TextField(blank=True, null=True)

    seller_username = models.CharField(max_length=100, blank=True, null=True)
    seller_feedback_score = models.IntegerField(blank=True, null=True)
    seller_feedback_percent = models.FloatField(blank=True, null=True)

    categories = models.JSONField(blank=True, null=True)

    marketplace = models.CharField(max_length=100, blank=True, null=True)

    item_country = models.CharField(max_length=2, blank=True, null=True)
    item_city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    item_created_at = models.DateTimeField(blank=True, null=True)

    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    sold_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "temp_summaries"

    def __str__(self):
        return self.title or self.ebay_item_id
