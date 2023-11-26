from django.contrib import admin
from products.models import Product, ProductTag

# Register your models here.
admin.site.register(ProductTag)
admin.site.register(Product)