from django.db import models
from common.models import TimeStampedModel
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    admin_user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)



