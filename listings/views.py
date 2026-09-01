from django.shortcuts import render
from django.views.generic import TemplateView, ListView

# Create your views here.

class Home(TemplateView):
    template_name = "listings/home.html"

class ListingsView(TemplateView):
    template_name = "listings/listings.html"
