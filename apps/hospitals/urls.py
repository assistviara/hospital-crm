from django.urls import path

from .views import hospital_list

app_name = "hospitals"

urlpatterns = [
    path("", hospital_list, name="hospital_list"),
]
