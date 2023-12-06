import requests

class RazorpayUtility:
    @staticmethod
    def create_order(client_order_id, notes, amount, currency):
        data = {
            "amount": amount,
            "currency": currency,
            "receipt": client_order_id,
            "notes": notes
        }
        headers = {}
        response = requests.post("https://api.razorpay.com/v1/orders", data=data, headers=headers)
        return response