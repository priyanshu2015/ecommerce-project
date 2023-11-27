from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from common.permissions import IsSuperUser
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
import os
import uuid
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateProductSerializer, ProductSerializer
from .models import Product
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.versioning import URLPathVersioning


class UploadProductImageView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    parser_classes = [MultiPartParser, ]

    def post(self, request, *args, **kwargs):
        img = request.data["image"]
        img_name = os.path.splitext(img.name)[0]
        img_extension = os.path.splitext(img.name)[1]

        save_path = "media/posts/post_images/"
        if not os.path.exists(save_path):
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

        image_name = img_name + str(uuid.uuid4())
        img_save_path = "%s/%s%s" % (save_path, image_name, img_extension)
        response_url = "posts/post_images/" + image_name + img_extension
        with open(img_save_path, "wb+") as f:
            for chunk in img.chunks():
                f.write(chunk)
        return Response({
            "path": response_url
        }, status=status.HTTP_200_OK)


# Create your views here.
class ListCreateProductView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["name", "tags__title"]
    ordering_fields = ["created_at", "updated_at", "id"]
    ordering = ["-created_at"]
    page_size = 2
    pagination_class = PageNumberPagination # LimitOffsetPagination
    # filterset_fields = ["admin_user_id", "admin_user__first_name", "tags__title"]
    filterset_fields = {
        "tags__title": ["exact", "in"],
        "created_at": ["exact", "gte", "lte"]
    }
    default_limit = 2
    max_limit = 10
    versioning_class = URLPathVersioning
    # ordering = id, search_field = name, page =2 => 

    def list(self, request, *args, **kwargs):
        self.pagination_class.page_size = self.page_size
        self.pagination_class.max_limit = self.max_limit
        self.pagination_class.default_limit = self.default_limit
        return super().list(request, *args, **kwargs)
    
    def get_serializer_class(self):
        print(self.request.version)
        if self.request.method == "POST":
            return CreateProductSerializer
        return ProductSerializer
    
    def get_queryset(self):
        # cache_data = cache.get(f'products')
        # if cache_data is not None:
        #     print("cache hit")
        #     return cache_data
        # else:
        products = Product.objects.filter().prefetch_related("tags")
        # cache.set("products", products, 100)
        return products
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={
            "request": request
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "payload": serializer.data,
                "status": "success",
                "message": "successfully created"
            },
            status=status.HTTP_201_CREATED, headers=headers)
    
