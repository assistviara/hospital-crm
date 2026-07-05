from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactPersonForm
from .models import ContactPerson


def contact_list(request):
    contacts = (
        ContactPerson.objects.filter(is_active=True)
        .select_related("hospital")
        .order_by("hospital__hospital_name", "name")
    )
    return render(request, "contacts/contact_list.html", {"contacts": contacts})


def contact_detail(request, pk):
    contact = get_object_or_404(
        ContactPerson.objects.select_related("hospital"),
        pk=pk,
        is_active=True,
    )
    return render(request, "contacts/contact_detail.html", {"contact": contact})


def contact_create(request):
    hospital_id = request.GET.get("hospital")
    if request.method == "POST":
        form = ContactPersonForm(request.POST, hospital_id=hospital_id)
        if form.is_valid():
            contact = form.save()
            messages.success(request, "担当者を登録しました。")
            return redirect("contacts:contact_detail", pk=contact.pk)
    else:
        form = ContactPersonForm(hospital_id=hospital_id)

    return render(
        request,
        "contacts/contact_form.html",
        {"form": form, "title": "担当者登録", "submit_label": "登録"},
    )


def contact_update(request, pk):
    contact = get_object_or_404(ContactPerson, pk=pk, is_active=True)
    if request.method == "POST":
        form = ContactPersonForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            messages.success(request, "担当者を更新しました。")
            return redirect("contacts:contact_detail", pk=contact.pk)
    else:
        form = ContactPersonForm(instance=contact)

    return render(
        request,
        "contacts/contact_form.html",
        {
            "form": form,
            "contact": contact,
            "title": "担当者編集",
            "submit_label": "更新",
        },
    )


def contact_delete(request, pk):
    contact = get_object_or_404(ContactPerson, pk=pk, is_active=True)
    if request.method == "POST":
        contact.is_active = False
        contact.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "担当者を削除しました。")
        return redirect("contacts:contact_list")

    return render(
        request,
        "contacts/contact_confirm_delete.html",
        {"contact": contact},
    )
