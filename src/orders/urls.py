from django.urls import path, include
from users.views import PlaceOrderView

urlpatterns = [
    path('', PlaceOrderView.as_view(), name="place-order"),
]
