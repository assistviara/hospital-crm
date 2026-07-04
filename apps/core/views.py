from django.shortcuts import render

from apps.corporations.models import Corporation
from apps.hospitals.models import Hospital
from apps.referrals.models import ReferralRecord
from apps.visits.models import VisitRecord


def dashboard(request):
    context = {
        "hospital_count": Hospital.objects.count(),
        "corporation_count": Corporation.objects.count(),
        "visit_count": VisitRecord.objects.count(),
        "referral_count": ReferralRecord.objects.count(),
    }
    return render(request, "dashboard.html", context)
