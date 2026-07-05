from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import VisitRecordForm
from .models import VisitRecord


def visit_list(request):
    visits = (
        VisitRecord.objects.filter(is_active=True)
        .select_related("hospital", "contact_person")
        .order_by("-visit_date", "hospital__hospital_name")
    )
    return render(request, "visits/visit_list.html", {"visits": visits})


def visit_detail(request, pk):
    visit = get_object_or_404(
        VisitRecord.objects.select_related("hospital__corporation", "contact_person"),
        pk=pk,
        is_active=True,
    )
    return render(request, "visits/visit_detail.html", {"visit": visit})


def visit_create(request):
    hospital_id = request.GET.get("hospital")
    if request.method == "POST":
        form = VisitRecordForm(request.POST, hospital_id=hospital_id)
        if form.is_valid():
            visit = form.save()
            messages.success(request, "訪問記録を登録しました。")
            return redirect("visits:visit_detail", pk=visit.pk)
    else:
        form = VisitRecordForm(hospital_id=hospital_id)

    return render(
        request,
        "visits/visit_form.html",
        {"form": form, "title": "訪問記録登録", "submit_label": "登録"},
    )


def visit_update(request, pk):
    visit = get_object_or_404(VisitRecord, pk=pk, is_active=True)
    if request.method == "POST":
        form = VisitRecordForm(request.POST, instance=visit)
        if form.is_valid():
            visit = form.save()
            messages.success(request, "訪問記録を更新しました。")
            return redirect("visits:visit_detail", pk=visit.pk)
    else:
        form = VisitRecordForm(instance=visit)

    return render(
        request,
        "visits/visit_form.html",
        {
            "form": form,
            "visit": visit,
            "title": "訪問記録編集",
            "submit_label": "更新",
        },
    )


def visit_delete(request, pk):
    visit = get_object_or_404(VisitRecord, pk=pk, is_active=True)
    if request.method == "POST":
        visit.is_active = False
        visit.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "訪問記録を削除しました。")
        return redirect("visits:visit_list")

    return render(
        request,
        "visits/visit_confirm_delete.html",
        {"visit": visit},
    )
