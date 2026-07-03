from django.db import models

from apps.contacts.models import ContactPerson
from apps.core.models import BaseModel
from apps.hospitals.models import Hospital


class VisitRecord(BaseModel):
    VISIT_METHOD_CHOICES = [
        ("visit", "訪問"),
        ("phone", "電話"),
        ("email", "メール"),
        ("online", "オンライン"),
        ("event", "研修・勉強会"),
        ("other", "その他"),
    ]

    INFORMATION_LEVEL_CHOICES = [
        ("official", "公式情報"),
        ("confirmed", "確認済み"),
        ("heard", "聞き取り"),
        ("rumor", "未確認"),
    ]

    FOLLOW_STATUS_CHOICES = [
        ("todo", "未対応"),
        ("doing", "対応中"),
        ("done", "完了"),
    ]

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="visit_records",
    )

    contact_person = models.ForeignKey(
        ContactPerson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visit_records",
    )

    visit_date = models.DateField()
    visit_method = models.CharField(
        max_length=50,
        choices=VISIT_METHOD_CHOICES,
        blank=True,
    )
    visitor_name = models.CharField(max_length=100, blank=True)

    summary = models.TextField(blank=True)
    positive_response = models.TextField(blank=True)
    concern = models.TextField(blank=True)
    next_action = models.TextField(blank=True)
    next_visit_date = models.DateField(null=True, blank=True)

    information_level = models.CharField(
        max_length=20,
        choices=INFORMATION_LEVEL_CHOICES,
        default="heard",
    )

    tags = models.CharField(max_length=500, blank=True)

    follow_status = models.CharField(
        max_length=20,
        choices=FOLLOW_STATUS_CHOICES,
        default="todo",
    )

    def __str__(self):
        return f"{self.visit_date} {self.hospital.hospital_name}"
