from django.shortcuts import render
from django.views.generic import TemplateView, ListView, RedirectView
from .models import Listing, PriceHistory, System

# Create your views here.

class Home(RedirectView):
    pattern_name = "listings"
    permanent = True

class ListingView(ListView):
    template_name = "listings/listings.html"
    context_object_name = "listings"
    paginate_by = 40

    def get_queryset(self):
        country = self.request.GET.get("country", "US")
        return Listing.objects.listings(country)

class PriceDropsView(ListView):
    template_name = "listings/pricedrops.html"
    paginate_by = 40
    #context_object_name = "drops"

    def get_queryset(self):
        country = self.request.GET.get("country", "US")
        return PriceHistory.objects.drops(country)    


#########


class SystemsView(ListView):
    model = System
    template_name = "listings/systems.html"

    # def get_queryset(self):
    #     country = self.request.GET.get("country", "US")
        # return Systems.objects.all_systems(country)
        

class SingleSystemView(ListView):
    template_name = "listings/system.html"
    context_object_name = "listings"
    paginate_by = 40

    def get_queryset(self):
        country = self.request.GET.get("country", "US")
        slug = self.kwargs["slug"]

        return (
            Listing.objects.filter(
                system__slug=slug,
                status="ACTIVE",
                country=country,
            )
            .select_related("system")
            .order_by("-last_updated")
        )

class AdvancedSearchView(TemplateView):
    template_name = "listings/advanced_search.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     country = self.request.GET.get("country", "US")

    #     context["country"] = country

    #     context["brands"] = CanonBrand.objects.all_brands(
    #         country=country
    #     )

    #     # Switches
    #     context["switches"] = get_specifications_in_yaml_order(
    #         "switch",
    #         "switches"
    #     )

    #     # Sizes
    #     context["sizes"] = get_specifications_in_yaml_order(
    #         "size",
    #         "sizes"
    #     )

    #     # Features
    #     context["features"] = get_specifications_in_yaml_order(
    #         "feature",
    #         "features"
    #     )

    #     return context


class SearchResultsView(ListView):
    template_name = "listings/search_results.html"
    context_object_name = "specs"
    paginate_by = 40

    # def get_queryset(self):
    #     country = self.request.GET.get("country", "US")

    #     brands = self.request.GET.getlist("brands")
    #     switches = self.request.GET.getlist("switches")
    #     sizes = self.request.GET.getlist("sizes")
    #     features = self.request.GET.getlist("features")

    #     return Specs.objects.advanced_search(
    #         country=country,
    #         brands=brands,
    #         switches=switches,
    #         sizes=sizes,
    #         features=features,
    #     )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        params = self.request.GET.copy()
        params.pop("page", None)

        context["search_params"] = params.urlencode()

        return context
    
    
class SearchView(ListView):
    model = Listing
    template_name = "listings/search.html"
    paginate_by = 40

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        country = self.request.GET.get("country", "US")

        queryset = Listing.objects.listings(country=country)

        if query:
            queryset = queryset.filter(title__icontains=query)

        return queryset

# static pages

class AboutView(TemplateView):
    template_name = "listings/about.html"


class HowItWorksView(TemplateView):
    template_name = "listings/how_it_works.html"


class AffiliateDisclosureView(TemplateView):
    template_name = "listings/affiliate_disclosure.html"


class DisclaimerView(TemplateView):
    template_name = "listings/disclaimer.html"


class PrivacyView(TemplateView):
    template_name = "listings/privacy.html"


class TermsView(TemplateView):
    template_name = "listings/terms.html"


class ContactView(TemplateView):
    template_name = "listings/contact.html"