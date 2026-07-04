from django.shortcuts import render

from apps.analytics.services import AnalyticsService
from apps.hospitals.models import Hospital


def analytics_list(request):
    hospitals = Hospital.objects.select_related("corporation").order_by("hospital_name")
    analytics_rows = [
        {
            "hospital": hospital,
            "analysis": AnalyticsService.analyze_hospital(hospital),
        }
        for hospital in hospitals
    ]
    return render(
        request,
        "analytics/analytics_list.html",
        {"analytics_rows": analytics_rows},
    )
