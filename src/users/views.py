from django.shortcuts import render
from rest_framework.views import APIView

from src.orders.choices import OrderStatusChoice
from .serializers import AddToCartRequestSerializer, DisplayCartSerializer
from products.models import Product
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from django.db.models import F
from rest_framework.generics import RetrieveAPIView
from orders.models import Order, OrderItem
from django.db import transaction
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
import razorpay
razorpay_client = razorpay.Client(auth=(settings.razorpay_id, settings.razorpay_account_id))

class ListProductsView(APIView):
    pass


class AddToCartView(APIView):
    serializer_class = AddToCartRequestSerializer

    def post(self,request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={
            "request": request
        })
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        product_uuid = validated_data["product_uuid"]
        product = Product.objects.filter(uuid=product_uuid).first()
        if product is None:
            return Response({
                "status": "error",
                "message": "Product not found",
                "payload": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        user_cart = Cart.objects.get_or_create(user=request.user)
        existing_cart_item = CartItem.objects.filter(
            cart=user_cart,
            product=product
        ).first()
        if existing_cart_item is not None:
            existing_cart_item.quantity = F("quantity") + 1
            existing_cart_item.save()
        else:
            cart_product = CartItem.objects.create(
                cart=user_cart,
                product=product,
                quantity=1
            )
        return Response({
            "status": "success",
            "message": "Successfully added the product to the cart",
            "payload": {}
        }, status=status.HTTP_200_OK)


class DisplayCartView(RetrieveAPIView):
    serializer_class = DisplayCartSerializer

    def get_object(self):
        cart = Cart.objects.filter(user=self.request.user).select_related("items__product")
        return cart


class RemoveProductFromCartView():
    pass


# Also cover offline cart as well
# class PlaceOrderView(APIView):

#     def post(self, request, *args, **kwargs):
#         with transaction.atomic():
#             # this lock in order to prevent any cart update while order creation
#             cart = Cart.objects.filter(user=request.user).select_for_update(nowait=True).first()
#             if cart is None:
#                 return Response({
#                     "status": "error",
#                     "message": "Cart is empty",
#                     "payload": {}
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             cart_items = CartItem.objects.filter(cart=cart)
#             final_price = 0
#             if(len(cart_items)<=0):
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
#             order_currency = 'INR'
#             callback_url = 'http://'+ str(get_current_site(request))+"/handlerequest/"
#             notes = {'order-type': "basic order from the website", 'key':'value'}
#             razorpay_order = razorpay_client.order.create(
#                 dict(amount=final_price*100, currency=order_currency, notes=notes, receipt=str(order.uuid), payment_capture='0'))
#             order.razorpay_order_id = razorpay_order['id']
#             order.save()
#             return Response({
#                 "status": "success",
#                 "message": "Order created succesfully, please proceed for payment",
#                 "payload": {
#                     'razorpay_order_id': razorpay_order['id'],
#                     'razorpay_merchant_id': settings.razorpay_id,
#                     'callback_url': callback_url,
#                     'final_price': final_price,
#                     "currency": order_currency
#                 }
#             })


# class HandleRazorpayPaymentCallback(APIView):

#     def post(self, request, *args, **kwargs):
#         razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
#         razorpay_order_id = request.POST.get('razorpay_order_id','')
#         razorpy_signature = request.POST.get('razorpay_signature','')
#         params_dict = {
#             'razorpay_order_id': razorpay_order_id,
#             'razorpay_payment_id': razorpay_payment_id,
#             'razorpay_signature': razorpy_signature
#         }
#         try:
#             order_ins = Order.objects.get(payment_gateway_order_id=razorpay_order_id)
#         except:
#             return HttpResponse("505 Not Found")
#         order_ins.payment_id = razorpay_payment_id
#         order_ins.razorpay_signature = signature
#         order_ins.save()
#         result = razorpay_client.utility.verify_payment_signature(params_dict)
#         if result==None:
#             amount = order_ins.amount * 100   #we have to pass in paisa
#             try:
#                 razorpay_client.payment.capture(razorpay_payment_id, amount)
#                 order_ins.payment_status = 1
#                 order_ins.save()

#                 ## For generating Invoice PDF
#                 template = get_template('firstapp/payment/invoice.html')
#                 data = {
#                     'order_id': order_db.order_id,
#                     'transaction_id': order_db.razorpay_payment_id,
#                     'user_email': order_db.user.email,
#                     'date': str(order_db.datetime_of_payment),
#                     'name': order_db.user.name,
#                     'order': order_db,
#                     'amount': order_db.total_amount,
#                 }
#                 html  = template.render(data)
#                 result = BytesIO()
#                 pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
#                 pdf = result.getvalue()
#                 filename = 'Invoice_' + data['order_id'] + '.pdf'

#                 mail_subject = 'Recent Order Details'
#                 # message = render_to_string('firstapp/payment/emailinvoice.html', {
#                 #     'user': order_db.user,
#                 #     'order': order_db
#                 # })
#                 context_dict = {
#                     'user': order_db.user,
#                     'order': order_db
#                 }
#                 template = get_template('firstapp/payment/emailinvoice.html')
#                 message  = template.render(context_dict)
#                 to_email = order_db.user.email
#                 # email = EmailMessage(
#                 #     mail_subject,
#                 #     message,
#                 #     settings.EMAIL_HOST_USER,
#                 #     [to_email]
#                 # )

#                 # for including css(only inline css works) in mail and remove autoescape off
#                 email = EmailMultiAlternatives(
#                     mail_subject,
#                     "hello",       # necessary to pass some message here
#                     settings.EMAIL_HOST_USER,
#                     [to_email]
#                 )
#                 email.attach_alternative(message, "text/html")
#                 email.attach(filename, pdf, 'application/pdf')
#                 email.send(fail_silently=False)

#                 return render(request, 'firstapp/payment/paymentsuccess.html',{'id':order_db.id})
#             except:
#                 order_db.payment_status = 2
#                 order_db.save()
#                 return render(request, 'firstapp/payment/paymentfailed.html')
#         else:
#             order_db.payment_status = 2
#             order_db.save()
#             return render(request, 'firstapp/payment/paymentfailed.html')