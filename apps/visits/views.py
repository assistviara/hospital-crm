from django.shortcuts import get_object_or_404, render

from .models import VisitRecord


def visit_list(request):
    visits = (
        VisitRecord.objects.select_related("hospital", "contact_person")
        .order_by("-visit_date", "hospital__hospital_name")
    )
    return render(request, "visits/visit_list.html", {"visits": visits})


def visit_detail(request, pk):
    visit = get_object_or_404(
        VisitRecord.objects.select_related("hospital__corporation", "contact_person"),
        pk=pk,
    )
    return render(request, "visits/visit_detail.html", {"visit": visit})
