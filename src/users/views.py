from django.shortcuts import render
from rest_framework.views import APIView
from users.serializers import AddToCartRequestSerializer, CartSerializer
from products.models import Product
from rest_framework.response import Response
from rest_framework import status
from users.models import Cart, CartItem
from django.db.models import F
from django.db import transaction
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class AddtoCartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartRequestSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        product_uuid = validated_data["product_uuid"]
        product = Product.objects.filter(uuid=product_uuid).first()
        if product is None:
            return Response({
                "status": "error",
                "message": "Product not found",
                "payload": {}
            }, status=status.HTTP_200)
        with transaction.atomic():
            cart = Cart.objects.filter(user=request.user).select_for_update(nowait=True).first()
            if cart is None:
                cart = Cart.objects.create(
                    user=request.user
                )
            existing_cart_item = CartItem.objects.filter(
                cart=cart,
                product=product
            ).first()
            if existing_cart_item is not None:
                existing_cart_item.quantity += 1
                existing_cart_item.save()
            else:
                cart_product = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=1
                )
            return Response({
                "status": "success",
                "message": "Successfully added the product to the cart",
                "payload": {}
            }, status=status.HTTP_200_OK)
            
            
class DisplayCartView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    
    def get_object(self):
        cart = Cart.objects.filter(user=self.request.user).prefetch_related("items__product").first()
        return cart
    

# class PlaceOrderView(APIView):
    
#     def post(self, request, *args, **kwargs):
#         with transaction.atomic():
#             cart = Cart.objects.filter(user=request.user).select_for_update(nowait=True).first()
#             if cart is None:
#                 return Response({
#                     "status": "error",
#                     "message": "Cart is empty",
#                     "payload": {}
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             cart_items = CartItem.objects.filter(cart=cart)
#             final_price = 0
#             if (len(cart_items) <= 0):
#                 return Response({
#                     "status": "error",
#                     "message": "Cart is empty",
#                     "payload": {}
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             order = Order.objects.create(
#                 user=request.user,
#                 amount=0,
#                 status=OrderStatusChoice.PENDING
#             )
#             for item in cart_items:
#                 order_item = OrderItem.objects.create(
#                     order=order,
#                     product=item.product,
#                     quantity=item.quantity,
#                     price=item.product.price
#                 )
#                 final_price = final_price + (item.product.price * item.quantity)
                
#             order.amount = final_price
#             order.save()
#             order_currency = "INR"
#             callback_url = ""
#             notes = {
                
#             }
#             try:
#                 razorpay_order_response = RazorpayUtility.create_order()
#                 if razorpay_order_response.ok:
#                     response_data = razorpay_order_response.json()
#                     razorpay_order_id = response_data["id"]
#                     order.provider_order_id = razorpay_order_id
#                     order.save()
#                     return Response({
#                         "status": "success",
#                         "message": "Order created successfully, please proceed for payment",
#                         "payload": {
#                             "order": {
#                                 "uuid": ""
#                             }
#                             "razorpay_order_id": razorpay_order_id,
#                             "razorpay_merchant_id": settings.RAZORPAY_MERCHANT_ID,
#                             # "callback_url": 
#                             "currency": order_currency
#                         }
#                     })
#             except Exception:
#                 return Response(
#                     {
#                         "status": "error"
#                     }
#                 )
            
        
        
# handler

# status of order/ details of particular order(retrieve order endpoint)