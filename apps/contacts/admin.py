from django.contrib import admin

from .models import ContactPerson


@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "hospital",
        "department",
        "position",
        "role",
        "phone",
        "email",
        "is_active",
    ]

    search_fields = [
        "name",
        "hospital__hospital_name",
        "department",
        "position",
        "role",
    ]

    list_filter = [
        "role",
        "is_active",
    ]
