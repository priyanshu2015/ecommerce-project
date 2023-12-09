import pytest
from rest_framework import status
from users.models import Cart, CartItem
import requests_mock
import requests
from orders.models import Order
from decimal import Decimal
import users
# from freezegun import freeze_time
# with freeze_time(lambda: frozen_time):


# @pytest.mark.usefixtures("create_feature_flag_rows")
@pytest.mark.django_db(reset_sequences=True)
class TestAddtoCartView:
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
            # product_uuid is not passed
            (1, {}, "product_uuid: This field is required."),
            # msg_hash is not passed
            (2, {
                "product_uuid": "123"
            }, "product_uuid: Must be a valid UUID."),
        ]
    )
    def test_response_is_400_when_request_params_incorrect(self, create_authenticated_client, create_user, request_id, request_params, error_message):
        user = create_user('1@2.com')
        client = create_authenticated_client(user)
        url = self.endpoint
        data = request_params
        response = client.post(url, data=data, format="json")
        # assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == "error"
        assert response.data["message"] == error_message

    def test_success_if_cart_exists(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2.com')
        cart = Cart.objects.create(user=user)
        client = create_authenticated_client(user)
        data = {
            "product_uuid": str(product.uuid)
        }
        url = self.endpoint
        response = client.post(url, data=data, format="json")
        assert response.data["status"] == "success"
        assert response.data["message"] == "Successfully added the product to the cart"
        carts = Cart.objects.all()
        assert carts.count() == 1
        assert carts.first().user == user
        cart_items = carts.first().items
        assert cart_items.first().quantity == 1

    def test_success_if_cart_not_exists(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2.com')
        client = create_authenticated_client(user)
        data = {
            "product_uuid": str(product.uuid)
        }
        url = self.endpoint
        response = client.post(url, data=data, format="json")
        assert response.data["status"] == "success"
        assert response.data["message"] == "Successfully added the product to the cart"
        carts = Cart.objects.all()
        assert carts.count() == 1
        assert carts.first().user == user
        cart_items = carts.first().items
        assert cart_items.first().quantity == 1

    def test_product_already_exist_in_cart(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2.com')
        cart = Cart.objects.create(user=user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )
        client = create_authenticated_client(user)
        data = {
            "product_uuid": str(product.uuid)
        }
        url = self.endpoint
        response = client.post(url, data=data, format="json")
        assert response.data["status"] == "success"
        assert response.data["message"] == "Successfully added the product to the cart"
        carts = Cart.objects.all()
        assert carts.count() == 1
        assert carts.first().user == user
        cart_items = carts.first().items
        assert cart_items.first().quantity == 2

    def test_product_does_not_exists(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2.com')
        cart = Cart.objects.create(user=user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )
        client = create_authenticated_client(user)
        data = {
            "product_uuid": "cb07815a-710b-4f45-a77f-9ae7486ee168"
        }
        url = self.endpoint
        response = client.post(url, data=data, format="json")
        assert response.data["status"] == "error"
        assert response.data["message"] == "Product not found"


def test_func_mock():
    print("function is mocked")


@pytest.mark.django_db(reset_sequences=True)
class TestPlaceOrderView:
    endpoint = '/orders/'

    def test_unauthenticated_users(self, create_unauthenticated_client):
        client = create_unauthenticated_client()
        url = self.endpoint
        data = {}
        response = client.post(url, data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_empty_cart(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2.com')
        client = create_authenticated_client(user)
        cart = Cart.objects.create(user=user)
        url = self.endpoint
        response = client.post(url, data={}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == "error"
        assert response.data["message"] == "Cart is empty"

    def test_success(self, create_product, create_user, create_authenticated_client, mocker):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user, price="1005")
        user = create_user('1@2.com')
        client = create_authenticated_client(user)
        cart = Cart.objects.create(user=user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2
        )

        sample_response = {
            "id": "order_NADHwDJpKtpVPt",
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
            "created_at": 1702117591
        }

        # mocks
        test_func_adapter = mocker.patch("users.views.test_func", test_func_mock)
        test_func_spy = mocker.spy(users.views, "test_func")
        url = "https://api.razorpay.com/v1/orders"
        with requests_mock.Mocker() as mock:
            mock.post(url, json=sample_response, status_code=200)
            url = self.endpoint
            response = client.post(url, data={}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        assert response.data["message"] == "Order created successfully, please proceed for payment"

        orders = Order.objects.all()
        assert orders.count() == 1
        order = orders.first()
        assert order.amount == Decimal("2010")
        assert order.status == "PENDING"

        # test_func_spy.assert_not_called()
        test_func_spy.assert_called_once()
        # test_func_spy.assert_called_once_with(**expected_params)
        # assert test_func_spy.spy_return == "TEST_SEND_SLACK_NOTIFICATION_MOCK"
        assert test_func_spy.call_count == 1
        # assert m_get_address_balance.call_args_list == expected_call_args_list