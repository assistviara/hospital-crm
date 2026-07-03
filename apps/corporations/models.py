from django.db import models

from apps.core.models import BaseModel


class Corporation(BaseModel):
    corporation_name = models.CharField(max_length=255)
    corporation_type = models.CharField(max_length=100, blank=True)
    homepage_url = models.URLField(blank=True)

    has_care_management = models.BooleanField(default=False)
    has_home_nursing = models.BooleanField(default=False)
    has_home_care = models.BooleanField(default=False)
    has_day_service = models.BooleanField(default=False)
    has_day_care = models.BooleanField(default=False)
    has_geriatric_health_facility = models.BooleanField(default=False)
    has_senior_housing = models.BooleanField(default=False)
    has_paid_nursing_home = models.BooleanField(default=False)

    def __str__(self):
        return self.corporation_name
