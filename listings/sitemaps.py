from django.contrib.sitemaps import Sitemap
from django.urls import reverse

# from .models import CanonBrand


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return [
            "index",
            # "listings",
            # "pricedrops",
            # "brands",
            # "about",
            # "how_it_works",
            # "affiliate_disclosure",
            # "disclaimer",
            # "privacy",
            # "terms",
            # "contact",
        ]

    def location(self, item):
        return reverse(item)


class BrandSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    # def items(self):
    #     return CanonBrand.objects.all()

    # def location(self, obj):
    #     return reverse("brand", kwargs={"slug": obj.slug})
