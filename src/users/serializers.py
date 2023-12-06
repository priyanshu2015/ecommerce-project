from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product


class AddToCartRequestSerializer(serializers.Serializer):
    product_uuid = serializers.CharField()
    
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "image",
            "uuid",
            "price"
        ]
    
    
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    
    class Meta:
        model = CartItem
        fields = [
            "quantity",
            "product"
        ]
    
    
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    
    class Meta:
        model = Cart
        fields = (
            "items",
        )