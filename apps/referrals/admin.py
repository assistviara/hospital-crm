from django.contrib import admin

from .models import ReferralRecord


@admin.register(ReferralRecord)
class ReferralRecordAdmin(admin.ModelAdmin):
    list_display = [
        "referral_date",
        "hospital",
        "service_type",
        "case_count",
        "contract_count",
        "care_manager_name",
        "is_active",
    ]

    search_fields = [
        "hospital__hospital_name",
        "hospital__corporation__corporation_name",
        "service_type",
        "care_manager_name",
    ]

    list_filter = [
        "service_type",
        "referral_date",
        "is_active",
    ]
