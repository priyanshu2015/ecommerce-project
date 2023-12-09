from rest_framework import status
import pytest
from orders.choices import OrderStatusChoice
from users.models import Cart, CartItem
import requests_mock
from orders.models import Order
from decimal import Decimal
import users
#from freezegun import freeze_time
#with freeze_time(lambda: frozen_time):
    


@pytest.mark.django_db(reset_sequences=True)
class TestAddToCartView:
    endpoint = "/addtocart/"
    
    def test_unauthenticated_users(self, create_unauthenticated_client):
        client = create_unauthenticated_client()
        url = self.endpoint
        data = {}
        response = client.post(url, data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.parametrize(
        "request_id, request_params, error_message",
        [
            (1, {}, "product_uuid: This field is required."),
            (2, {
                "product_uuid": "1233"
            }, "product_uuid: Must be a valid UUID.")
        ]
    )      
    def test_response_is_400_when_request_params_incorrect(self, create_authenticated_client, create_user, request_id, request_params, error_message):
        user = create_user("1@2.com")
        client = create_authenticated_client(user)
        url = self.endpoint
        data = request_params
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == "error"
        assert response.data["message"] == error_message
        
    def test_success_if_cart_exists(self, create_authenticated_client, create_user, create_product):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2gmail.com')
        cart = Cart.objects.create(
            user=user
        )
        data = {
            "product_uuid": str(product.uuid)
        }
        url = self.endpoint
        client = create_authenticated_client(user=user)
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        carts = Cart.objects.all()
        assert carts.count() == 1
        cart_items = carts.first().items
        assert cart_items.count() == 1
        assert cart_items.first().quantity == 1
        
    def test_success_if_cart_not_exists(self, create_authenticated_client, create_user, create_product):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2gmail.com')
        data = {
            "product_uuid": str(product.uuid)
        }
        url = self.endpoint
        client = create_authenticated_client(user=user)
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        carts = Cart.objects.all()
        assert carts.count() == 1
        assert carts.first().user == user
        cart_items = carts.first().items
        assert cart_items.count() == 1
        assert cart_items.first().quantity == 1
        
    def test_product_does_not_exists(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2gmail.com')
        data = {
            "product_uuid": "1865c841-2494-46ee-9582-cbefa89078ca"
        }
        url = self.endpoint
        client = create_authenticated_client(user=user)
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["status"] == "error"
        assert response.data["message"] == "Product not found"
        
    def test_product_already_exist_in_cart(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2gmail.com')
        cart = Cart.objects.create(
            user=user
        )
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product
        )
        data = {
            "product_uuid": str(product.uuid)
        }
        url = self.endpoint
        client = create_authenticated_client(user=user)
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        carts = Cart.objects.all()
        assert carts.count() == 1
        assert carts.first().user == user
        cart_items = carts.first().items
        assert cart_items.count() == 1
        assert cart_items.first().quantity == 2
        
        
def test_func_mock(a, b):
    print("function is mocked")
    return a + b
        
        
@pytest.mark.django_db(reset_sequences=True)
class TestPlaceOrderView:
    endpoint = "/orders/"
    
    def test_unauthenticated_users(self, create_unauthenticated_client):
        client = create_unauthenticated_client()
        url = self.endpoint
        data = {}
        response = client.post(url, data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_cart_does_not_exists(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2gmail.com')
        url = self.endpoint
        data = {}
        client = create_authenticated_client(user=user)
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == "error"
        assert response.data["message"] == "Cart is empty"
        
    def test_empty_cart(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2gmail.com')
        cart = Cart.objects.create(
            user=user
        )
        url = self.endpoint
        data = {}
        client = create_authenticated_client(user=user)
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == "error"
        assert response.data["message"] == "Cart is empty"
        
    def test_success(self, create_product, create_user, create_authenticated_client, mocker):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user, price="1005")
        product_2 = create_product(admin_user=admin_user, price="1000")
        user = create_user('1@2gmail.com')
        cart = Cart.objects.create(
            user=user
        )
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2
        )
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product_2,
            quantity=1
        )
        url = self.endpoint
        data = {}
        
        # mocks
        test_func_adapter = mocker.patch("users.views.test_func", test_func_mock)
        
        test_func_spy = mocker.spy(users.views, "test_func")
        
        sample_response = {
            "id": "order_NAGMZtkVcLIjap",
            "entity": "order",
            "amount": 10000,
            "amount_paid": 0,
            "amount_due": 10000,
            "currency": "INR",
            "receipt": "92f9a408-fd3e-407d-8168-d4a7476a4f2f",
            "offer_id": None,
            "status": "created",
            "attempts": 0,
            "notes": {},
            "created_at": 1702128420
        }
        client = create_authenticated_client(user=user)
        url = "https://api.razorpay.com/v1/orders"
        with requests_mock.Mocker() as mock:
            mock.post(url, json=sample_response, status_code=200)
            
            response = client.post(self.endpoint, data={}, format="json")
            
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        assert response.data["message"] == "Order created successfully, please proceed for payment"
        
        orders = Order.objects.all()
        assert orders.count() == 1
        order = orders.first()
        assert order.amount == Decimal("3010")
        assert order.status == OrderStatusChoice.PENDING
        assert order.provider_order_id == "order_NAGMZtkVcLIjap"
        assert order.items.count() == 2
        
        test_func_spy.assert_called_once()
        
        assert test_func_spy.call_count == 1
        
        expected_params = {
            "a": 10,
            "b": 20
        }
        
        test_func_spy.assert_called_once_with(**expected_params)
        assert test_func_spy.spy_return == 30
        
        
        