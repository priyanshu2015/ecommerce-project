from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from products.models import Product
from .serializers import ProductCreateSerializer, ProductSerializer, ProductImageSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import os
import uuid
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsSuperUser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.versioning import URLPathVersioning, NamespaceVersioning, QueryParameterVersioning


class ProductImageUpload(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        print(request.data)
        print(request.POST)
        print(request.FILES)
        img = request.data["image"]
        img_name = os.path.splitext(img.name)[0]
        img_extension = os.path.splitext(img.name)[1]

        # This will generate random folder for saving your image using UUID
        save_path = "media/" + "posts/post_images/"
        if not os.path.exists(save_path):
            # This will ensure that the path is created properly and will raise exception if the directory already exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Create image save path with title
        image_name = img_name + str(uuid.uuid4())
        img_save_path = "%s/%s%s" % (save_path, image_name, img_extension)

        response_url = "posts/post_images/" + image_name + img_extension
        with open(img_save_path, "wb+") as f:
            for chunk in img.chunks():
                f.write(chunk)
        return Response({
            "path": response_url
        }, status=status.HTTP_200_OK)


class ListCreateProductView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    serializer_class = ProductSerializer
    # parser_classes = [MultiPartParser]
    pagination_class = LimitOffsetPagination # PageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    # filterset_fields = ["admin_user_id", "admin_user__first_name", "tags__title", "uuid"]
    filterset_fields = {
        "tags__title": ["exact", "in"],  # ?access_state__in=RESTRICTED,PUBLIC
        # ?tags__title__in=RESTRICTED,PUBLIC&access__is_owner=False --> for shared by others
        # 'access__is_owner': ["exact"]
        "name": ["exact", "in"],
        "created_at": ["gte", "lte"],
        "updated_at": ["gte", "lte"],
    }
    search_fields = ["name", "tags__title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    page_size = 1
     # default_limit has precedence over default_limit
    default_limit = 5
    max_limit = 20
    versioning_class = NamespaceVersioning

    def list(self, request, *args, **kwargs):
        self.pagination_class.page_size = self.page_size
        self.pagination_class.max_limit = self.max_limit
        self.pagination_class.default_limit = self.default_limit
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        print("hello")
        print(self.request.version)
        if self.request.method == "POST":
            return ProductCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self, queryset = None):
        return Product.objects.filter().prefetch_related("tags")

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# if only file upload + normal data => use form request
# if both file upload + nested serializer data
# => use separate file upload and then pass url in data
# => base64.b64encode(file.read()).decode('utf-8') and then pass file in json
# => use separate file upload for file upload and normal data and separate endpoint for nested data
# => Use a custom multipart json serializer https://stackoverflow.com/questions/30176570/using-django-rest-framework-how-can-i-upload-a-file-and-send-a-json-payload

