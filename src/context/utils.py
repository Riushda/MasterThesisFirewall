import numpy as np


def get_device(field):
    key_list = field.split(".")
    return key_list[0]


def get_device_field(field):
    key_list = field.split(".")
    if len(key_list) > 1:
        return key_list[1]
    else:
        return None


def is_member(field, member_list):
    key_list = field.split(".")
    return key_list[0] in member_list


def get_element(self, json, field):
    element = None
    key_list = field.split(".")
    for key in key_list:
        if element:
            element = element[key]
        else:
            element = json[key]

    return element


def flatten_state(state):
    flattened = {}
    for device in state:
        for field in state[device]:
            flat_field = device + "." + field
            flattened[flat_field] = state[device][field]

    return flattened


def unflatten_state(state):
    unflattened = {}
    for key in state:
        device = get_device(key)
        field = get_device_field(key)
        if not unflattened.get(device):
            unflattened[device] = {}

        unflattened[device][field] = state[key]

    return unflattened


class Categorizer:

    def __init__(self):
        self.mapping = {}

    def add_mapping(self, field, intervals, labels):
        d = dict(enumerate(labels, 1))
        self.mapping[field] = {}
        self.mapping[field]["categorizer"] = np.vectorize(d.get)
        self.mapping[field]["intervals"] = intervals

    def remove_mapping(self, field):
        self.mapping.pop(field)

    def update_mapping(self, field, intervals, labels):
        self.remove_mapping(field)
        self.add_mapping(field, intervals, labels)

    def has_mapping(self, field):
        return self.mapping.get(field) is not None

    def map(self, field, value):
        categorizer = self.mapping[field]["categorizer"]
        intervals = self.mapping[field]["intervals"]

        result = categorizer(np.digitize(value, intervals))  # also work with array

        return result.__str__()
