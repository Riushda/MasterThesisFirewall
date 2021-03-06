"""
This file contains the class responsible for categorizing floating values into labels. It also defines the context
input, which uses the previously parsed input to build the necessary data structures used to initialize the context.
"""

import numpy as np

from client.handler import Handler
from context.utils import flatten_state
from client.constant import *


class Categorization:

    def __init__(self):
        self.mapping = {}

    def __str__(self):
        return str(self.mapping)

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

        result = categorizer(np.digitize(value, intervals))

        return result.__str__()


def convert_inference(member_key, member):
    field = list(member)[0]
    name = member_key + "." + field
    value = member[field]
    return [name, value]


class ContextInput:
    def __init__(self, handler: Handler):
        self.triggers = handler.triggers
        self.categorization = Categorization()
        self.initial_state = {}
        self.state_combinations = {}
        self.state_inference = {}
        self.inconsistent_states = []
        self.relations = handler.relations
        self.members = handler.members
        self.time_intervals = handler.time_intervals
        self.relation_mapping = handler.relation_mapping
        self.convert_input(handler.categorization, handler.members, handler.inferences, handler.inconsistencies)

    def __str__(self):
        result = f"Triggers: {self.triggers}\n"
        result += f"Categorization: {self.categorization}\n"
        result += f"State combinations: {self.state_combinations}\n"
        result += f"Initial state: {self.initial_state}\n"
        result += f"State inference: {self.state_inference}\n"
        result += f"Inconsistent states: {self.inconsistent_states}\n"
        return result

    def convert_input(self, labels, members, inferences, inconsistencies):
        for trigger in self.triggers:
            trigger["condition"] = flatten_state(trigger["condition"])

        for member_key, member in members.items():
            for field_key, field in member.fields.items():
                name = member_key + "." + field_key
                if field.f_type == FieldType.DEC:
                    label = field.value
                    self.categorization.add_mapping(name, labels[label][0], labels[label][1])
                    self.state_combinations[name] = labels[label][1]
                elif field.f_type == FieldType.STR:
                    self.state_combinations[name] = field.value
                self.initial_state[name] = field.init

        for inference in inferences:
            member_key = list(inference["condition"])[0]
            member = convert_inference(member_key, inference["condition"][member_key])
            implication = []

            for implication_key in inference["implication"].keys():
                implication.append(convert_inference(implication_key, inference["implication"][implication_key]))

            self.state_inference[(member[0], member[1])] = implication

        for i in range(len(inconsistencies)):
            self.inconsistent_states.append(flatten_state(inconsistencies[i]))
