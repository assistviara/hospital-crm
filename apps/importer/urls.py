from django.urls import path

from . import views

app_name = "importer"

urlpatterns = [
    path("hospitals/csv/", views.hospital_csv_import, name="hospital_csv_import"),
    path(
        "hospitals/csv/import/",
        views.hospital_csv_import_execute,
        name="hospital_csv_import_execute",
    ),
    path(
        "hospitals/csv/session/create/",
        views.hospital_csv_session_create,
        name="hospital_csv_session_create",
    ),
    path("hospitals/csv/review/", views.hospital_csv_review, name="hospital_csv_review"),
    path("hospitals/pdf/", views.hospital_pdf_convert, name="hospital_pdf_convert"),
    path("sessions/", views.import_session_list, name="import_session_list"),
    path("sessions/<int:pk>/", views.import_session_detail, name="import_session_detail"),
    path("sessions/<int:pk>/apply/", views.import_session_apply, name="import_session_apply"),
]
