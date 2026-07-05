from django import forms

from apps.contacts.models import ContactPerson
from apps.hospitals.models import Hospital
from .models import VisitRecord


class VisitRecordForm(forms.ModelForm):
    class Meta:
        model = VisitRecord
        fields = [
            "hospital",
            "contact_person",
            "visit_date",
            "visit_method",
            "visitor_name",
            "summary",
            "positive_response",
            "concern",
            "next_action",
            "next_visit_date",
            "information_level",
            "tags",
            "follow_status",
            "memo",
        ]
        widgets = {
            "visit_date": forms.DateInput(attrs={"type": "date"}),
            "next_visit_date": forms.DateInput(attrs={"type": "date"}),
            "summary": forms.Textarea(attrs={"rows": 4}),
            "positive_response": forms.Textarea(attrs={"rows": 3}),
            "concern": forms.Textarea(attrs={"rows": 3}),
            "next_action": forms.Textarea(attrs={"rows": 3}),
            "memo": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        hospital_id = kwargs.pop("hospital_id", None)
        super().__init__(*args, **kwargs)
        self.fields["hospital"].queryset = Hospital.objects.filter(
            is_active=True
        ).order_by("hospital_name")
        self.fields["contact_person"].queryset = ContactPerson.objects.filter(
            is_active=True
        ).select_related("hospital").order_by("hospital__hospital_name", "name")
        if hospital_id:
            self.fields["hospital"].initial = hospital_id
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select"})
            else:
                field.widget.attrs.update({"class": "form-control"})
