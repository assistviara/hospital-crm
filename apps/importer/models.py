from django.db import models

from apps.hospitals.models import Hospital


class ImportSession(models.Model):
    SOURCE_TYPE_PDF = "pdf"
    SOURCE_TYPE_CSV = "csv"
    SOURCE_TYPE_API = "api"
    SOURCE_TYPE_MANUAL = "manual"
    SOURCE_TYPE_CHOICES = [
        (SOURCE_TYPE_PDF, "PDF"),
        (SOURCE_TYPE_CSV, "CSV"),
        (SOURCE_TYPE_API, "API"),
        (SOURCE_TYPE_MANUAL, "手動"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_REVIEWING = "reviewing"
    STATUS_APPLIED = "applied"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "下書き"),
        (STATUS_REVIEWING, "レビュー中"),
        (STATUS_APPLIED, "反映済み"),
        (STATUS_FAILED, "失敗"),
    ]

    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default=SOURCE_TYPE_CSV,
    )
    source_name = models.CharField(max_length=255, blank=True)
    source_file_path = models.CharField(max_length=500, blank=True)
    converted_csv_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    total_count = models.IntegerField(default=0)
    new_count = models.IntegerField(default=0)
    update_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    applied_count = models.IntegerField(default=0)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        created_at = self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "-"
        source_name = self.source_name or "名称未設定"
        return f"{created_at} {source_name}"


class ImportRecord(models.Model):
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_ERROR = "error"
    ACTION_SKIP = "skip"
    ACTION_TYPE_CHOICES = [
        (ACTION_CREATE, "新規"),
        (ACTION_UPDATE, "更新"),
        (ACTION_ERROR, "エラー"),
        (ACTION_SKIP, "スキップ"),
    ]

    session = models.ForeignKey(
        ImportSession,
        on_delete=models.CASCADE,
        related_name="records",
    )
    row_number = models.IntegerField(default=0)
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPE_CHOICES,
        default=ACTION_CREATE,
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_records",
    )
    hospital_name = models.CharField(max_length=255)
    corporation_name = models.CharField(max_length=255, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    diff_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    is_selected = models.BooleanField(default=True)
    is_applied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.row_number}: {self.hospital_name}"
