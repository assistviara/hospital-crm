from django.urls import path

from .views import visit_list

app_name = "visits"

urlpatterns = [
    path("", visit_list, name="visit_list"),
]
