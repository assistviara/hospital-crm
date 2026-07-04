from django.urls import path

from .views import corporation_list

app_name = "corporations"

urlpatterns = [
    path("", corporation_list, name="corporation_list"),
]
