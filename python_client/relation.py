from rule import Rule
from constant import *


class Relation():
    def __init__(self, first: Rule, second: Rule = None, context: list = []):
        self.has_broker = 0
        if(second):
            self.has_broker = 1
        self.first = first
        self.second = second
        self.context = context

    def __str__(self):
        if(self.second):
            return f"{self.first} ~ {self.second}"
        else:
            return f"{self.first}"

    def to_bytes(self):
        s_constraints = []
        for x in range(0, len(self.context)):
            if(not self.context[x].type in D_CONSTRAINT._value2member_map_):
                s_constraints.append(x)

        buffer = bytearray()

        buffer += self.has_broker.to_bytes(1, 'little')
        buffer += self.first.to_bytes()

        if(self.second):
            buffer += self.second.to_bytes()
        buffer += len(s_constraints).to_bytes(1, 'little')

        for x in s_constraints:
            buffer += self.context[x].to_bytes()

        return buffer
