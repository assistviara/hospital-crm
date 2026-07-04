from django.shortcuts import render

from django.db.models import Count

from .models import Corporation


def corporation_list(request):
    corporations = (
        Corporation.objects.annotate(hospital_count=Count("hospitals"))
        .order_by("corporation_name")
    )
    return render(
        request,
        "corporations/corporation_list.html",
        {"corporations": corporations},
    )
