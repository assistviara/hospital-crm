from django.urls import path

from . import views

app_name = "importer"

urlpatterns = [
    path("hospitals/csv/", views.hospital_csv_import, name="hospital_csv_import"),
]
