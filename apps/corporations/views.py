from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from django.db.models import Count, Q

from .forms import CorporationForm
from .models import Corporation


def corporation_list(request):
    corporations = (
        Corporation.objects.filter(is_active=True)
        .annotate(hospital_count=Count("hospitals", filter=Q(hospitals__is_active=True)))
        .order_by("corporation_name")
    )
    return render(
        request,
        "corporations/corporation_list.html",
        {"corporations": corporations},
    )


def corporation_detail(request, pk):
    corporation = get_object_or_404(Corporation, pk=pk, is_active=True)
    hospitals = corporation.hospitals.filter(is_active=True).order_by("hospital_name")
    return render(
        request,
        "corporations/corporation_detail.html",
        {"corporation": corporation, "hospitals": hospitals},
    )


def corporation_create(request):
    if request.method == "POST":
        form = CorporationForm(request.POST)
        if form.is_valid():
            corporation = form.save()
            messages.success(request, "法人を登録しました。")
            return redirect("corporations:corporation_detail", pk=corporation.pk)
    else:
        form = CorporationForm()

    return render(
        request,
        "corporations/corporation_form.html",
        {"form": form, "title": "法人登録", "submit_label": "登録"},
    )


def corporation_update(request, pk):
    corporation = get_object_or_404(Corporation, pk=pk, is_active=True)
    if request.method == "POST":
        form = CorporationForm(request.POST, instance=corporation)
        if form.is_valid():
            corporation = form.save()
            messages.success(request, "法人を更新しました。")
            return redirect("corporations:corporation_detail", pk=corporation.pk)
    else:
        form = CorporationForm(instance=corporation)

    return render(
        request,
        "corporations/corporation_form.html",
        {
            "form": form,
            "corporation": corporation,
            "title": "法人編集",
            "submit_label": "更新",
        },
    )


def corporation_delete(request, pk):
    corporation = get_object_or_404(Corporation, pk=pk, is_active=True)
    if request.method == "POST":
        corporation.is_active = False
        corporation.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "法人を削除しました。")
        return redirect("corporations:corporation_list")

    return render(
        request,
        "corporations/corporation_confirm_delete.html",
        {"corporation": corporation},
    )
