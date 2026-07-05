from django import forms

from apps.corporations.models import Corporation
from .models import Hospital


class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = [
            "corporation",
            "hospital_name",
            "address",
            "phone",
            "fax",
            "homepage_url",
            "total_beds",
            "general_beds",
            "chronic_beds",
            "psychiatric_beds",
            "community_beds",
            "recovery_beds",
            "disability_beds",
            "other_beds",
            "has_regional_cooperation",
            "regional_department_name",
            "msw_count",
            "discharge_nurse_count",
            "memo",
        ]
        widgets = {
            "memo": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["corporation"].queryset = Corporation.objects.filter(
            is_active=True
        ).order_by("corporation_name")
        _apply_bootstrap_widgets(self.fields)


def _apply_bootstrap_widgets(fields):
    for field in fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs.update({"class": "form-check-input"})
        elif isinstance(field.widget, forms.Select):
            field.widget.attrs.update({"class": "form-select"})
        else:
            field.widget.attrs.update({"class": "form-control"})
