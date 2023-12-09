import pytest
from rest_framework.test import APIClient
import shortuuid

from .factories import ProductFactory


@pytest.fixture
def api_client():
    return APIClient


@pytest.fixture
def create_unauthenticated_client(api_client):
    def make_unauthenticated_client() -> APIClient:
        return api_client()

    return make_unauthenticated_client


@pytest.fixture
def create_authenticated_client(api_client):
    def make_authenticated_client(user) -> APIClient:
        client = api_client()
        client.force_authenticate(user=user)
        return client

    return make_authenticated_client


@pytest.fixture
def test_password():
    return 'password-123'


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(email, **kwargs):
        """
        kwargs requires the following params:
            - email

        kwargs can include
            - username
        """
        kwargs["password"] = test_password
        if "username" not in kwargs:
            """
            uuid4() gives dashes in between, shotuuid is used on usersignup view too.
            #Validation Error: Username must only contain numbers, underscores and letters
            # kwargs['username'] = str(uuid.uuid4())
            """
            kwargs['username'] = shortuuid.uuid()
        kwargs["email"] = email
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def create_product(db):
    def make_product(**kwargs):
        product = ProductFactory(**kwargs)
        print(product)
        return product

    return make_product