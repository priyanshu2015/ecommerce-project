from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from products.models import Product
from .serializers import PostCreateSerializer, ProductSerializer, ProductImageSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import os
import uuid


class ProductImageUpload(APIView):
    permission_classes = []
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
    permission_classes = []
    serializer_class = ProductSerializer
    # parser_classes = [MultiPartParser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self, queryset = None):
        return Product.objects.filter().order_by("-created_at").prefetch_related("tags")

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