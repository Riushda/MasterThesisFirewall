from utils.constant import *


class Constraint:
    def __init__(self, f_type: FieldType, field: str, value: list):
        self.f_type = f_type
        self.field = field
        self.value = value

    def __str__(self):
        return f"type: {self.f_type.value} | field: {self.field} | value: {self.value}"
