from django.db import models
from django.db.models import Window, ExpressionWrapper, FloatField, F
from django.db.models.functions import Lag


class ListingQuerySet(models.QuerySet):
    def filter_country(self, country):
        if country:
            return self.filter(country=country)
        return self


class ListingManager(models.Manager):
    def get_queryset(self):
        return ListingQuerySet(self.model, using=self._db)

    def listings(self, country=None):
        return (
            self.get_queryset()
            .filter(status="ACTIVE")
            .filter_country(country)
            .order_by("-last_updated")
        )

class PriceHistoryManager(models.Manager):

    def drops(self, country=None):
        queryset = (
            self.get_queryset()
            .filter(
                listing__status="ACTIVE",
            )
            .annotate(
                old_price=Window(
                    expression=Lag("price"),
                    partition_by=[F("listing")],
                    order_by=[
                        F("recorded_at").asc(),
                        F("id").asc(),
                    ],
                )
            )
            .filter(
                old_price__isnull=False,
                price__lt=F("old_price"),
            )
            .annotate(
                discount_percent=ExpressionWrapper(
                    (F("old_price") - F("price")) * 100 / F("old_price"),
                    output_field=FloatField(),
                )
            )
            .select_related("listing")
        )

        if country:
            queryset = queryset.filter(listing__country=country)

        return queryset.order_by("-discount_percent")
