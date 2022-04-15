from client.handler import Handler
from utils.constant import *


class ContextInput:
    def __init__(self, handler: Handler):
        self.abstract_rules = []
        self.categorization = []
        self.initial_state = {}
        self.state_combinations = {}
        self.state_inference = []
        self.inconsistent_states = []
        self.convert_input(handler.labels, handler.members, handler.relations, handler.triggers)

    def __str__(self):
        result = f"Abstract rules: {self.abstract_rules}\n"
        result += f"Categorization: {self.categorization}\n"
        result += f"State combinations: {self.state_combinations}\n"
        result += f"Initial state: {self.initial_state}"
        return result

    def convert_input(self, labels, members, relations, triggers):
        self.abstract_rules = triggers

        for member_key, member in members.items():
            self.state_combinations[member_key] = {}
            self.initial_state[member_key] = {}
            for field_key, field in member.field.items():
                if field["type"] == FieldType.INT.value:
                    label = field["label"]
                    name = f"{member_key}.{label}"
                    category = [name, labels[label]]
                    self.categorization.append(category)
                    self.state_combinations[member_key][field_key] = labels[label][1]
                elif field["type"] == FieldType.STR.value:
                    self.state_combinations[member_key][field_key] = field["value"]
                self.initial_state[member_key][field_key] = field["init"]
