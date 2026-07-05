from django import forms

from apps.hospitals.models import Hospital
from .models import ContactPerson


class ContactPersonForm(forms.ModelForm):
    class Meta:
        model = ContactPerson
        fields = [
            "hospital",
            "name",
            "department",
            "position",
            "role",
            "phone",
            "email",
            "preferred_contact_method",
            "memo",
        ]
        widgets = {
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
