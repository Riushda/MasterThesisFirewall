def get_device_name(ip, members):
    for device_key, device in members.items():
        if device.ip == ip:
            return device_key

    return None


def get_device(field):
    key_list = field.split(".")
    return key_list[0]


def is_float(string):
    try:
        float(string)
    except ValueError:
        return False
    return True


def flatten_state(state):
    flattened = {}
    for device in state:
        for field in state[device]:
            flat_field = device + "." + field
            flattened[flat_field] = state[device][field]

    return flattened
