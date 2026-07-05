from django.contrib import admin

from apps.importer.models import ImportRecord, ImportSession


@admin.register(ImportSession)
class ImportSessionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "source_type",
        "source_name",
        "status",
        "total_count",
        "new_count",
        "update_count",
        "error_count",
        "applied_count",
        "created_at",
    ]
    list_filter = [
        "source_type",
        "status",
        "created_at",
    ]
    search_fields = [
        "source_name",
        "source_file_path",
        "converted_csv_path",
        "note",
    ]


@admin.register(ImportRecord)
class ImportRecordAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "session",
        "row_number",
        "action_type",
        "hospital_name",
        "corporation_name",
        "hospital",
        "is_selected",
        "is_applied",
    ]
    list_filter = [
        "action_type",
        "is_selected",
        "is_applied",
        "session",
    ]
    search_fields = [
        "hospital_name",
        "corporation_name",
        "error_message",
    ]
