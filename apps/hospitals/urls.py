from django.urls import path

from . import views

app_name = "hospitals"

urlpatterns = [
    path("", views.hospital_list, name="hospital_list"),
    path("<int:pk>/", views.hospital_detail, name="hospital_detail"),
]
