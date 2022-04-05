import numpy as np
import json
import os

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


def is_float(string):
    try:
        float(string)
    except ValueError:
        return False
    return True


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


class InputParser:
    def __init__(self):
        self.dirname = os.path.dirname(__file__)

    def input_path(self, input: str):
        return f"{self.dirname}/input/{input}.json"

    def load_json(self, input: str):
        return json.load(open(self.input_path(input)))

    def get_input(self):
        initial_state = flatten_state(self.load_json("initial_state"))

        state_combinations = flatten_state(self.load_json("state_combinations"))

        inconsistent_states = self.load_json("inconsistent_states")
        for i in range(len(inconsistent_states)):
            inconsistent_states[i] = flatten_state(inconsistent_states[i])

        inference_array = self.load_json("state_inference")
        state_inference = {}
        for inference in inference_array:
            state_inference[(inference["key"][0], inference["key"][1])] = inference["value"]

        abstract_rules = self.load_json("abstract_rules")
        for rule in abstract_rules:
            rule["condition"] = flatten_state(rule["condition"])

        categorization = self.load_json("categorization")

        return initial_state, state_combinations, inconsistent_states, state_inference, abstract_rules, categorization


class Categorizer:

    def __init__(self):
        self.mapping = {}

    def add_mapping(self, field, intervals, labels):
        d = dict(enumerate(labels, 1))
        self.mapping[field] = {}
        self.mapping[field]["categorizer"] = np.vectorize(d.get)

        for i in range(len(intervals)):
            intervals[i] = float(intervals[i])

        self.mapping[field]["intervals"] = intervals

    def add_mapping_array(self, mapping_array):
        for mapping in mapping_array:
            self.add_mapping(mapping[0], mapping[1], mapping[2])

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