from django.db import models
from django.utils import timezone

# Create your models here.

CURRENCY_SYMBOLS = {
    "USD": "$",
    "AUD": "$",
    "GBP": "£",
    "EUR": "€",
}

class PriceDrop(models.Model):
    id = models.BigIntegerField(primary_key=True)
    ebay_item_id = models.CharField(max_length=255)
    title = models.TextField()
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    image_urls = models.JSONField()
    condition = models.CharField(max_length=255)
    country = models.CharField(max_length=10)
    status = models.CharField(max_length=20)
    affiliate_url = models.TextField()
    last_updated = models.DateTimeField()
    discount_percent = models.FloatField()

    class Meta:
        db_table = "lf_price_drops"

    @property
    def currency_symbol(self):
        return CURRENCY_SYMBOLS.get(self.currency, self.currency)
