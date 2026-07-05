from django import forms

from apps.hospitals.models import Hospital
from .models import ReferralRecord


class ReferralRecordForm(forms.ModelForm):
    class Meta:
        model = ReferralRecord
        fields = [
            "hospital",
            "referral_date",
            "service_type",
            "case_count",
            "contract_count",
            "care_manager_name",
            "memo",
        ]
        widgets = {
            "referral_date": forms.DateInput(attrs={"type": "date"}),
            "memo": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        hospital_id = kwargs.pop("hospital_id", None)
        super().__init__(*args, **kwargs)
        self.fields["hospital"].queryset = Hospital.objects.filter(
            is_active=True
        ).order_by("hospital_name")
        if hospital_id:
            self.fields["hospital"].initial = hospital_id
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select"})
            else:
                field.widget.attrs.update({"class": "form-control"})
