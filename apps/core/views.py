from django.shortcuts import render

from apps.analytics.services import AnalyticsService
from apps.corporations.models import Corporation
from apps.hospitals.models import Hospital
from apps.referrals.models import ReferralRecord
from apps.visits.models import VisitRecord


def dashboard(request):
    rank_counts = {"S": 0, "A": 0}
    for hospital in Hospital.objects.select_related("corporation"):
        rank = AnalyticsService.analyze_hospital(hospital)["rank"]
        if rank in rank_counts:
            rank_counts[rank] += 1

    context = {
        "hospital_count": Hospital.objects.count(),
        "corporation_count": Corporation.objects.count(),
        "visit_count": VisitRecord.objects.count(),
        "referral_count": ReferralRecord.objects.count(),
        "s_rank_hospital_count": rank_counts["S"],
        "a_rank_hospital_count": rank_counts["A"],
        "unvisited_hospital_count": Hospital.objects.filter(visit_records__isnull=True).count(),
        "incomplete_follow_count": VisitRecord.objects.filter(
            follow_status__in=["todo", "doing"]
        ).count(),
    }
    return render(request, "dashboard.html", context)
