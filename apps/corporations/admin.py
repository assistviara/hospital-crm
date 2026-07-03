from django.contrib import admin

from .models import Corporation


@admin.register(Corporation)
class CorporationAdmin(admin.ModelAdmin):
    list_display = [
        "corporation_name",
        "corporation_type",
        "has_care_management",
        "has_home_nursing",
        "has_geriatric_health_facility",
        "has_senior_housing",
        "has_paid_nursing_home",
        "is_active",
    ]

    search_fields = [
        "corporation_name",
        "corporation_type",
    ]

    list_filter = [
        "has_care_management",
        "has_home_nursing",
        "has_geriatric_health_facility",
        "has_senior_housing",
        "has_paid_nursing_home",
        "is_active",
    ]
