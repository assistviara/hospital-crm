from django.urls import path

from . import views

app_name = "hospitals"

urlpatterns = [
    path("", views.hospital_list, name="hospital_list"),
    path("create/", views.hospital_create, name="hospital_create"),
    path("<int:pk>/edit/", views.hospital_update, name="hospital_update"),
    path("<int:pk>/delete/", views.hospital_delete, name="hospital_delete"),
    path("<int:pk>/", views.hospital_detail, name="hospital_detail"),
]
