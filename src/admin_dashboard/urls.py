from django.urls import path, include, re_path
from products.views import ListCreateProductView, ProductImageUpload


urlpatterns = [
    re_path('^(?P<version>(v1|v2))/products/$', ListCreateProductView.as_view(), name='list-create-product'),
    path('products/image_upload/', ProductImageUpload.as_view(), name='product-image-upload')
]
