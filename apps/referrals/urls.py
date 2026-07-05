from django.urls import path

from . import views

app_name = "referrals"

urlpatterns = [
    path("", views.referral_list, name="referral_list"),
    path("create/", views.referral_create, name="referral_create"),
    path("<int:pk>/edit/", views.referral_update, name="referral_update"),
    path("<int:pk>/delete/", views.referral_delete, name="referral_delete"),
    path("<int:pk>/", views.referral_detail, name="referral_detail"),
]
