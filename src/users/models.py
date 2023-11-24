from django.db import models
from django.contrib.auth import get_user_model
from common.models import TimeStampedModel
from products.models import Product

User = get_user_model()


class Cart(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)



