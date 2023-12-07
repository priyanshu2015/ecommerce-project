@pytest.fixture
def create_user(db, create_user):
    def make_dex_user(eth_address, stark_key, **kwargs):
        email = f"{eth_address}@{settings.EMAIL_DOMAIN}"
        user = create_user(email=email, **kwargs)
        CustomerProfileFactory(user=user, stark_key=stark_key)
        return user

    return make_dex_user


@pytest.fixture
def create_user_cart(db, create_user):
    def make_dex_user(eth_address, stark_key, **kwargs):
        email = f"{eth_address}@{settings.EMAIL_DOMAIN}"
        user = create_user(email=email, **kwargs)
        CustomerProfileFactory(user=user, stark_key=stark_key)
        return user

    return make_dex_user