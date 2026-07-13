from django.contrib import admin

from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    search_fields = ("question", "answer")
    list_editable = ("is_active",)
    fields = ("question", "answer", "category", "is_active")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # The matcher caches a fitted TF-IDF model in memory for speed.
        # Any add/edit/toggle in the admin must invalidate that cache so
        # the chatbot picks up the change on its very next request.
        from .nlp_matcher import invalidate_matcher_cache
        invalidate_matcher_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        from .nlp_matcher import invalidate_matcher_cache
        invalidate_matcher_cache()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        from .nlp_matcher import invalidate_matcher_cache
        invalidate_matcher_cache()
