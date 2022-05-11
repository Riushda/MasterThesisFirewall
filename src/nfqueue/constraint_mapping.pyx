from utils.constant import *


class MappingEntry:
    def __init__(self, subject: str, constraints: list):
        self.subject = subject
        self.constraints = constraints


def match_constraint(field: str, value: str, constraints: list):
    for c in constraints:
        if field == c.field:
            if c.f_type == FieldType.DEC:
                for interval in c.value:
                    try:
                        if interval[0] <= float(value) <= interval[1]:
                            return True
                    except ValueError:
                        return False
            elif c.f_type == FieldType.STR:
                if value in c.value:
                    return True
                else:
                    return False
    return False

def match_packet(packet, mapping_entry):
    if packet.subject != mapping_entry.subject:
        return False

    # No constraint on this relation
    if len(mapping_entry.constraints) == 0:
        return True

    for data in packet.content:
        if len(data) > 1:
            if not match_constraint(data[0], data[1], mapping_entry.constraints):
                return False
        else:
            return False

    return True


class ConstraintMapping:
    def __init__(self):
        self.mapping = {}

    def add_mapping(self, mark: int, entry: MappingEntry):
        self.mapping[mark] = entry

    def del_mapping(self, mark: int):
        del self.mapping[mark]

    def get_mapping(self, mark: int):
        return self.mapping[mark]

    def decision(self, packet):
        mapping_entry = self.mapping[packet.mark]
        if match_packet(packet, mapping_entry):
            print("Match!")
            return Policy.ACCEPT
        else:
            print("No match!")
            return Policy.DROP
