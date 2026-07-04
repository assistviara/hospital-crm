from django.urls import path

from . import views

app_name = "corporations"

urlpatterns = [
    path("", views.corporation_list, name="corporation_list"),
    path("<int:pk>/", views.corporation_detail, name="corporation_detail"),
]
