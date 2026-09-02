from django.shortcuts import render
from django.views.generic import TemplateView, ListView, RedirectView
from .models import Listing, PriceHistory

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
