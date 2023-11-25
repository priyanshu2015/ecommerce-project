def validation_error_handler(data):
    key = list(data.keys())[0]
    value = data[key]
    if type(value) == list:
        message = f"{key}: {value[0]}"
    else:
        message = f"{key}: {value}"
    return message