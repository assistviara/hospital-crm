from django.db import models

from apps.core.models import BaseModel
from apps.corporations.models import Corporation


class Hospital(BaseModel):
    corporation = models.ForeignKey(
        Corporation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hospitals",
    )

    hospital_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    homepage_url = models.URLField(blank=True)

    total_beds = models.IntegerField(default=0)
    general_beds = models.IntegerField(default=0)
    chronic_beds = models.IntegerField(default=0)
    psychiatric_beds = models.IntegerField(default=0)
    community_beds = models.IntegerField(default=0)
    recovery_beds = models.IntegerField(default=0)
    disability_beds = models.IntegerField(default=0)
    other_beds = models.IntegerField(default=0)

    has_regional_cooperation = models.BooleanField(default=False)
    regional_department_name = models.CharField(max_length=255, blank=True)

    msw_count = models.IntegerField(default=0)
    discharge_nurse_count = models.IntegerField(default=0)

    def __str__(self):
        return self.hospital_name
