from django import forms

from .models import Corporation


class CorporationForm(forms.ModelForm):
    class Meta:
        model = Corporation
        fields = [
            "corporation_name",
            "corporation_type",
            "homepage_url",
            "has_care_management",
            "has_home_nursing",
            "has_home_care",
            "has_day_service",
            "has_day_care",
            "has_geriatric_health_facility",
            "has_senior_housing",
            "has_paid_nursing_home",
            "memo",
        ]
        widgets = {
            "memo": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                field.widget.attrs.update({"class": "form-control"})
