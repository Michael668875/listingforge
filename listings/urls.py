from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.Home.as_view(), name="index"),
    path("listings/", views.ListingView.as_view(), name="listings"),
    path("pricedrops/", views.PriceDropsView.as_view(), name="pricedrops"),
    path(
    "robots.txt",
            TemplateView.as_view(
                template_name="listings/robots.txt",
                content_type="text/plain"
            ),
            name="robots",
        ),
]