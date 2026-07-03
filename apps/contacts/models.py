from django.db import models

from apps.core.models import BaseModel
from apps.hospitals.models import Hospital


class ContactPerson(BaseModel):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="contact_persons",
    )

    name = models.CharField(max_length=100)
    department = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)

    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    preferred_contact_method = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name}（{self.hospital.hospital_name}）"
