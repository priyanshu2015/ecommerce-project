from django.db import models
from django.db.models.query import QuerySet
from authentication.models import User


class CustomerSupportManager(models.Manager):
    def get_queryset(self, *args, **kwargs) -> QuerySet:
        return super().get_queryset(*args, **kwargs).filter(is_customer_support_user=True)


# Create your models here.
class CustomerSupportUser(User):

    class Meta:
        proxy = True
    
    @property
    def showAdditional(self):
        return self.customer_support_additional


class CustomerSupportUserAdditional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_support_additional")
    # add any other extra field here related to Customer Support User