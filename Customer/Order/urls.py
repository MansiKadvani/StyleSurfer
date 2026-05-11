from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

######################################################################################
######################################################################################

urlpatterns = [
    path("order_form/", views.order_form, name="order_form"),
    path("order_success/<str:order_id>/", views.order_success, name="order_success"),
    path("create_checkout_session/", views.create_checkout_session, name="create_checkout_session"),
    path("payment_success/<str:order_id>/", views.payment_success, name="payment_success"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

######################################################################################
######################################################################################
