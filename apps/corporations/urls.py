from django.urls import path

from . import views

app_name = "corporations"

urlpatterns = [
    path("", views.corporation_list, name="corporation_list"),
    path("create/", views.corporation_create, name="corporation_create"),
    path("<int:pk>/edit/", views.corporation_update, name="corporation_update"),
    path("<int:pk>/delete/", views.corporation_delete, name="corporation_delete"),
    path("<int:pk>/", views.corporation_detail, name="corporation_detail"),
]
