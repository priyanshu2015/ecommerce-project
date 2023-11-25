from django.db import models
from common.models import TimeStampedModel
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

class Tag(TimeStampedModel):
    title = models.CharField(unique=True, max_length=100)

    def __str__(self) -> str:
        return "#" + self.title

    def clean(self) -> None:
        self.title = self.title.lower()
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Product(TimeStampedModel):
    image = models.ImageField(upload_to='products/product_images', null=True, blank=True)
    name = models.CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    admin_user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, through="ProductTag", related_name="products")


class ProductTag(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product_id', 'tag_id'], name='unique_product_tag'
            )
        ]
