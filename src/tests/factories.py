import factory
from products.models import Product
from datetime import datetime
from authentication.models import User

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
    admin_user = factory.SubFactory(AdminUserFactory) # , factory_related_name="products")
    name = factory.Sequence(lambda n: 'product-name-{}'.format(n))
    price = factory.Faker('pyint', min_value=0, max_value=100000)
    
    class Meta:
        model = Product