COUNTRIES = [
    ("AU", "🇦🇺 Australia"),
    ("US", "🇺🇸 United States"),
    ("GB", "🇬🇧 United Kingdom"),
    ("CA", "🇨🇦 Canada"),
    ("IE", "🇮🇪 Ireland"),
]

def country_context(request):
    return {
        "selected_country": request.GET.get("country", "US"),
        "countries": COUNTRIES,
    }
