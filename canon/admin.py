from django.contrib import admin

from .models import TitleCleanupTerm

# Register your models here.

@admin.register(TitleCleanupTerm)
class TitleCleanupTermAdmin(admin.ModelAdmin):
    list_display = ("term", "category")
    list_filter = ("category",)
    search_fields = ("terms",)
    ordering = ("category", "term")


