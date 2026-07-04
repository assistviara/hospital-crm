from django.shortcuts import get_object_or_404, render

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


def corporation_detail(request, pk):
    corporation = get_object_or_404(Corporation, pk=pk)
    hospitals = corporation.hospitals.order_by("hospital_name")
    return render(
        request,
        "corporations/corporation_detail.html",
        {"corporation": corporation, "hospitals": hospitals},
    )
