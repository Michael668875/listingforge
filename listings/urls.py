from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.Home.as_view(), name="index"),
    path("listings/", views.ListingView.as_view(), name="listings"),
    path("pricedrops/", views.PriceDropsView.as_view(), name="pricedrops"),
    path("systems/", views.SystemsView.as_view(), name="systems"),    
    path("systems/<slug:slug>/", views.SingleSystemView.as_view(), name="system"),    
    path("advanced_search/", views.AdvancedSearchView.as_view(), name="advanced_search"),    
    path("search/", views.SearchView.as_view(), name="search"),
    path("search-results", views.SearchResultsView.as_view(), name="search_results"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("how-it-works/", views.HowItWorksView.as_view(), name="how_it_works"),
    path("affiliate-disclosure/", views.AffiliateDisclosureView.as_view(), name="affiliate_disclosure"),
    path("disclaimer/", views.DisclaimerView.as_view(), name="disclaimer"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("terms/", views.TermsView.as_view(), name="terms"),
    path("contact/", views.ContactView.as_view(), name="contact"),

    path(
    "robots.txt",
            TemplateView.as_view(
                template_name="listings/robots.txt",
                content_type="text/plain"
            ),
            name="robots",
        ),
]