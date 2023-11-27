from django.urls import path, include, re_path
from products.views import UploadProductImageView, ListCreateProductView

urlpatterns = [
    path('products/image_upload/', UploadProductImageView.as_view(), name='product-image-upload'),
    # path('products/', ListCreateProductView.as_view(), name="list-create-product")
    re_path(
        r'^(?P<version>(v1|v2))/products/$',
        ListCreateProductView.as_view(),
        name='list-create-product'
    ),
]