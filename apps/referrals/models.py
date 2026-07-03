from django.db import models

from apps.core.models import BaseModel
from apps.hospitals.models import Hospital


class ReferralRecord(BaseModel):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="referral_records",
    )

    referral_date = models.DateField()
    service_type = models.CharField(max_length=100, blank=True)
    case_count = models.IntegerField(default=0)
    contract_count = models.IntegerField(default=0)
    care_manager_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.referral_date} {self.hospital.hospital_name} {self.case_count}件"
