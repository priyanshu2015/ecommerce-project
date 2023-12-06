from django.urls import path, include
from . import views

urlpatterns = [
    path('addtocart/', views.AddtoCartView.as_view(), name="add-to-cart"),
    path('cart/', views.DisplayCartView.as_view(), name="display-cart")
]
