from utils.constant import *


class Field:
    def __init__(self, f_type: FieldType, value, init: str):
        self.f_type = f_type
        self.value = value
        self.init = init
