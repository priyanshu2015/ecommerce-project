from datetime import datetime
import factory
import factory.django
import faker
from faker import Faker
from authentication.models import User
from products.models import Product
import random

MIN_PRICE = 100
MAX_PRICE = 10000

class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: 'test-email@example.com'.format(n))
    username = factory.Sequence(lambda n: 'user{}'.format(n))
    is_active = True
    is_staff = False
    is_superuser = False
    date_joined = factory.LazyFunction(datetime.now)

    class Meta:
        model = User


class AdminUserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: 'test-email@example.com'.format(n))
    username = factory.Sequence(lambda n: 'user{}'.format(n))
    is_active = True
    is_staff = True
    is_superuser = True
    date_joined = factory.LazyFunction(datetime.now)

    class Meta:
        model = User



class ProductFactory(factory.django.DjangoModelFactory):
    admin_user = factory.SubFactory(AdminUserFactory, factory_related_name="products")
    name = factory.Sequence(lambda n: 'product-name-{}'.format(n))
    # price = factory.LazyAttribute(random.randrange(MIN_PRICE, MAX_PRICE + 1))
    # price = factory.fuzzy.FuzzyDecimal(low=MIN_PRICE, high=MAX_PRICE, precision=2)
    # price = 100
    price = factory.Faker('pyint', min_value=0, max_value=1000)

    class Meta:
        model = Product