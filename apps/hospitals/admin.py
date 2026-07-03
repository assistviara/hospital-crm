from django.contrib import admin

from .models import Hospital


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = [
        "hospital_name",
        "corporation",
        "total_beds",
        "community_beds",
        "recovery_beds",
        "chronic_beds",
        "psychiatric_beds",
        "msw_count",
        "discharge_nurse_count",
        "is_active",
    ]

    search_fields = [
        "hospital_name",
        "corporation__corporation_name",
        "regional_department_name",
    ]

    list_filter = [
        "has_regional_cooperation",
        "is_active",
    ]
