

@pytest.mark.django_db(reset_sequences=True)
class TestAddToCartView:
    endpoint = "/sapi/v1/user/balance/"

    def test_unauthenticated_client(self, create_unauthenticated_client, create_user):
        client = create_unauthenticated_client()
        url = self.endpoint
        data = {}
        response = client.get(url, data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "request_id, request_params, error_message",
        [
            (1, {
                "currency": "efg",
            }, "please enter a valid currency"),
        ]
    )
    def test_response_is_400_when_request_params_incorrect(self, create_authenticated_client, create_user, request_id, request_params, error_message):
        user_email = "user@email.com"
        user = create_user(email=user_email)
        client = create_authenticated_client(user)
        response = client.get(path=self.endpoint,
                              data=request_params, format="json")
        assert response.data == {
            "status": "error",
            "message": error_message,
            "payload": ""
        }
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "status": "error",
            "message": error_message,
            "payload": ""
        }

    def test_product_already_present_in_cart(self, create_authenticated_client, create_user, mocker):
        user_email = "user@email.com"
        user = create_user(email=user_email)
        client = create_authenticated_client(user)

        # mock
        peatio_utility_mock = mocker.patch(
            "user_details.views.Utility",
            UtilityMock,
        )

        # act
        response = client.get(path=self.endpoint,
                              data=request_params, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "status": "success",
            "message": "Retrieved Successfully",
            "payload": {
                "currency": "eth",
                "balance": "0.1959644",
                "locked": "0.0"
            }
        }

    def test_product_not_present_in_cart():
        pass


# @pytest.mark.usefixtures("create_feature_flag_rows")