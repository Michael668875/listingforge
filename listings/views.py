from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .models import TempSummary

# Create your views here.

class Home(TemplateView):
    template_name = "listings/home.html"

class ListingsView(ListView):
    model = TempSummary
    template_name = "listings/listings.html"

    context_object_name = "listings"
