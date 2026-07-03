from django.contrib import admin

from .models import VisitRecord


@admin.register(VisitRecord)
class VisitRecordAdmin(admin.ModelAdmin):
    list_display = [
        "visit_date",
        "hospital",
        "contact_person",
        "visit_method",
        "visitor_name",
        "information_level",
        "follow_status",
        "next_visit_date",
        "is_active",
    ]

    search_fields = [
        "hospital__hospital_name",
        "hospital__corporation__corporation_name",
        "contact_person__name",
        "visitor_name",
        "summary",
        "tags",
    ]

    list_filter = [
        "visit_method",
        "information_level",
        "follow_status",
        "visit_date",
        "next_visit_date",
        "is_active",
    ]
