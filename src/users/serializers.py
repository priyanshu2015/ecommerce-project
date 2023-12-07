from rest_framework import serializers
from orders.models import Order, OrderItem
from .models import Cart, CartItem
from products.models import Product


class AddToCartRequestSerializer(serializers.Serializer):
    product_uuid = serializers.UUIDField()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "image",
            "name",
            "price"
        )


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = (
            "product",
            "quantity"
        )


class DisplayCartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = (
            "items"
        )


class RazorpayDetailsSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    callback_url = serializers.CharField()
    merchant_id = serializers.CharField()


class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "image",
            "name"
        )


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer()
    class Meta:
        model = OrderItem
        fields = (
            "product",
            "price",
            "quantity"
        )


class CreateOrderResponseSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            "uuid",
            "amount",
            "status"
        )