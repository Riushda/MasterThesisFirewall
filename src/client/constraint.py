from utils.constant import *


class Constraint:
    def __init__(self, c_type: ConstraintType, field: str, value: list):
        self.c_type = c_type
        self.field = field
        self.value = value

    def __str__(self):
        return f"type: {self.c_type.value} | field: {self.field} | value: {self.value}"
