from django.urls import path
from . import views

#######################################################################################################################
#######################################################################################################################

urlpatterns = [

    path("buy_backS/", views.buy_backS, name="buy_backS"),

    path("accept-request/<str:buyback_id>/", views.accept_request, name="accept_request"),

    path("send_customization_done/<str:buyback_id>/", views.send_customization_done, name="send_customization_done"),

    path("reject-request/<str:buyback_id>/", views.reject_request, name="reject_request"),

    path("customization_details/<str:buyback_id>/", views.customization_details, name="customization_details"),
]

#######################################################################################################################
