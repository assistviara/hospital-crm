from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReferralRecordForm
from .models import ReferralRecord


def referral_list(request):
    referrals = (
        ReferralRecord.objects.filter(is_active=True)
        .select_related("hospital")
        .order_by("-referral_date", "hospital__hospital_name")
    )
    return render(request, "referrals/referral_list.html", {"referrals": referrals})


def referral_detail(request, pk):
    referral = get_object_or_404(
        ReferralRecord.objects.select_related("hospital"),
        pk=pk,
        is_active=True,
    )
    return render(request, "referrals/referral_detail.html", {"referral": referral})


def referral_create(request):
    hospital_id = request.GET.get("hospital")
    if request.method == "POST":
        form = ReferralRecordForm(request.POST, hospital_id=hospital_id)
        if form.is_valid():
            referral = form.save()
            messages.success(request, "紹介記録を登録しました。")
            return redirect("referrals:referral_detail", pk=referral.pk)
    else:
        form = ReferralRecordForm(hospital_id=hospital_id)

    return render(
        request,
        "referrals/referral_form.html",
        {"form": form, "title": "紹介記録登録", "submit_label": "登録"},
    )


def referral_update(request, pk):
    referral = get_object_or_404(ReferralRecord, pk=pk, is_active=True)
    if request.method == "POST":
        form = ReferralRecordForm(request.POST, instance=referral)
        if form.is_valid():
            referral = form.save()
            messages.success(request, "紹介記録を更新しました。")
            return redirect("referrals:referral_detail", pk=referral.pk)
    else:
        form = ReferralRecordForm(instance=referral)

    return render(
        request,
        "referrals/referral_form.html",
        {
            "form": form,
            "referral": referral,
            "title": "紹介記録編集",
            "submit_label": "更新",
        },
    )


def referral_delete(request, pk):
    referral = get_object_or_404(ReferralRecord, pk=pk, is_active=True)
    if request.method == "POST":
        referral.is_active = False
        referral.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "紹介記録を削除しました。")
        return redirect("referrals:referral_list")

    return render(
        request,
        "referrals/referral_confirm_delete.html",
        {"referral": referral},
    )
