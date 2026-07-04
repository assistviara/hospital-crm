from django.urls import path

from . import views

app_name = "visits"

urlpatterns = [
    path("", views.visit_list, name="visit_list"),
    path("<int:pk>/", views.visit_detail, name="visit_detail"),
]
