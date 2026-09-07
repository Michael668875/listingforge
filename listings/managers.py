from django.db import models
from django.db.models import ExpressionWrapper, FloatField, F, OuterRef, Subquery, FloatField

from django.db import models
from django.db.models import (
    F,
    OuterRef,
    Subquery,
    ExpressionWrapper,
    FloatField,
)
from django.apps import apps

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

    def drops(self, country=None):

        PriceHistory = apps.get_model("listings", "PriceHistory")

        # Oldest recorded PriceHistory price for each listing
        first_price = (
            PriceHistory.objects
            .filter(listing=OuterRef("pk"))
            .order_by("recorded_at", "id")
            .values("price")[:1]
        )

        queryset = (
            self.get_queryset()
            .filter(status="ACTIVE")
            .annotate(
                old_price=Subquery(first_price),
            )
            .filter(
                old_price__gt=F("price"),
            )
            .annotate(
                discount_percent=ExpressionWrapper(
                    (F("old_price") - F("price")) * 100
                    / F("old_price"),
                    output_field=FloatField(),
                )
            )
        )

        if country:
            queryset = queryset.filter(country=country)

        return queryset.order_by("-discount_percent")

# class PriceHistoryManager(models.Manager):

#     def drops(self, country=None):
#         queryset = (
#             self.get_queryset()
#             .filter(
#                 listing__status="ACTIVE",
#             )
#             .annotate(
#                 old_price=Window(
#                     expression=Lag("price"),
#                     partition_by=[F("listing")],
#                     order_by=[
#                         F("recorded_at").asc(),
#                         F("id").asc(),
#                     ],
#                 )
#             )
#             .filter(
#                 old_price__isnull=False,
#                 price__lt=F("old_price"),
#             )
#             .annotate(
#                 discount_percent=ExpressionWrapper(
#                     (F("old_price") - F("price")) * 100 / F("old_price"),
#                     output_field=FloatField(),
#                 )
#             )
#             .select_related("listing")
#         )

#         if country:
#             queryset = queryset.filter(listing__country=country)

#         return queryset.order_by("-discount_percent")



# class PriceHistoryManager(models.Manager):

#     def drops(self, country=None):

#         first_price = (
#             self.get_queryset()
#             .filter(listing_id=OuterRef("listing_id"))
#             .order_by("recorded_at", "id")
#             .values("price")[:1]
#         )

#         queryset = (
#             self.get_queryset()
#             .filter(
#                 listing__status="ACTIVE",
#             )
#             .annotate(
#                 old_price=Subquery(first_price),
#             )
#             .filter(
#                 old_price__gt=F("listing__price"),
#             )
#             .annotate(
#                 discount_percent=ExpressionWrapper(
#                     (F("old_price") - F("listing__price")) * 100
#                     / F("old_price"),
#                     output_field=FloatField(),
#                 )
#             )
#             .select_related("listing")
#         )

#         if country:
#             queryset = queryset.filter(
#                 listing__country=country
#             )

#         return queryset.order_by("-discount_percent")


# class PriceHistoryManager(models.Manager):

#     def drops(self, country=None):

#         # Oldest recorded PriceHistory price for each listing
#         first_price = (
#             self.get_queryset()
#             .filter(listing_id=OuterRef("pk"))
#             .order_by("recorded_at", "id")
#             .values("price")[:1]
#         )

#         queryset = (
#             Listing.objects
#             .filter(status="ACTIVE")
#             .annotate(
#                 old_price=Subquery(first_price),
#             )
#             .filter(
#                 old_price__gt=F("price"),
#             )
#             .annotate(
#                 discount_percent=ExpressionWrapper(
#                     (F("old_price") - F("price")) * 100
#                     / F("old_price"),
#                     output_field=FloatField(),
#                 )
#             )
#         )

#         if country:
#             queryset = queryset.filter(country=country)

#         return queryset.order_by("-discount_percent")