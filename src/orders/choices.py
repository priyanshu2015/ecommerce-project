class OrderStatusChoice:
    PENDING = "PENDING"
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    CANCELLED = "CANCELLED"
    SUCCESS = "SUCCESS"

    CHOICE_LIST = [
        (PENDING, PENDING),
        (PAYMENT_SUCCESS, PAYMENT_SUCCESS),
        (CANCELLED, CANCELLED),
        (SUCCESS, SUCCESS)
    ]