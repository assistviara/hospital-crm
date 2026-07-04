from django.shortcuts import render

from .models import Hospital


def hospital_list(request):
    hospitals = Hospital.objects.select_related("corporation").order_by("hospital_name")
    return render(request, "hospitals/hospital_list.html", {"hospitals": hospitals})
