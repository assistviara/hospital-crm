from django.shortcuts import get_object_or_404, render

from apps.analytics.services import AnalyticsService
from apps.referrals.models import ReferralRecord
from apps.visits.models import VisitRecord
from .models import Hospital


def hospital_list(request):
    hospitals = Hospital.objects.select_related("corporation").order_by("hospital_name")
    return render(request, "hospitals/hospital_list.html", {"hospitals": hospitals})


def hospital_detail(request, pk):
    hospital = get_object_or_404(
        Hospital.objects.select_related("corporation"),
        pk=pk,
    )
    contact_persons = hospital.contact_persons.order_by("name")
    visits = (
        VisitRecord.objects.filter(hospital=hospital)
        .select_related("contact_person")
        .order_by("-visit_date")
    )
    referrals = ReferralRecord.objects.filter(hospital=hospital).order_by("-referral_date")
    context = {
        "hospital": hospital,
        "contact_persons": contact_persons,
        "visits": visits,
        "referrals": referrals,
        "analysis": AnalyticsService.analyze_hospital(hospital),
    }
    return render(request, "hospitals/hospital_detail.html", context)
