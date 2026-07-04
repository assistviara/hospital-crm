from django.shortcuts import render

from .models import VisitRecord


def visit_list(request):
    visits = (
        VisitRecord.objects.select_related("hospital", "contact_person")
        .order_by("-visit_date", "hospital__hospital_name")
    )
    return render(request, "visits/visit_list.html", {"visits": visits})
