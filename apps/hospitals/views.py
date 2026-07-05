from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.analytics.services import AnalyticsService
from apps.referrals.models import ReferralRecord
from apps.visits.models import VisitRecord
from .forms import HospitalForm
from .models import Hospital


def hospital_list(request):
    hospitals = (
        Hospital.objects.filter(is_active=True)
        .select_related("corporation")
        .order_by("hospital_name")
    )
    return render(request, "hospitals/hospital_list.html", {"hospitals": hospitals})


def hospital_detail(request, pk):
    hospital = get_object_or_404(
        Hospital.objects.select_related("corporation"),
        pk=pk,
        is_active=True,
    )
    contact_persons = hospital.contact_persons.filter(is_active=True).order_by("name")
    visits = (
        VisitRecord.objects.filter(hospital=hospital, is_active=True)
        .select_related("contact_person")
        .order_by("-visit_date")
    )
    referrals = ReferralRecord.objects.filter(
        hospital=hospital,
        is_active=True,
    ).order_by("-referral_date")
    context = {
        "hospital": hospital,
        "contact_persons": contact_persons,
        "visits": visits,
        "referrals": referrals,
        "analysis": AnalyticsService.analyze_hospital(hospital),
    }
    return render(request, "hospitals/hospital_detail.html", context)


def hospital_create(request):
    if request.method == "POST":
        form = HospitalForm(request.POST)
        if form.is_valid():
            hospital = form.save()
            messages.success(request, "病院を登録しました。")
            return redirect("hospitals:hospital_detail", pk=hospital.pk)
    else:
        form = HospitalForm()

    return render(
        request,
        "hospitals/hospital_form.html",
        {"form": form, "title": "病院登録", "submit_label": "登録"},
    )


def hospital_update(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk, is_active=True)
    if request.method == "POST":
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            hospital = form.save()
            messages.success(request, "病院を更新しました。")
            return redirect("hospitals:hospital_detail", pk=hospital.pk)
    else:
        form = HospitalForm(instance=hospital)

    return render(
        request,
        "hospitals/hospital_form.html",
        {
            "form": form,
            "hospital": hospital,
            "title": "病院編集",
            "submit_label": "更新",
        },
    )


def hospital_delete(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk, is_active=True)
    if request.method == "POST":
        hospital.is_active = False
        hospital.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "病院を削除しました。")
        return redirect("hospitals:hospital_list")

    return render(
        request,
        "hospitals/hospital_confirm_delete.html",
        {"hospital": hospital},
    )
