from utils.constant import *
from utils.lock_dictionary import LockDictionary


class MappingEntry:
    def __init__(self, subject: str, constraints: list, policy: Policy):
        self.subject = subject
        self.constraints = constraints
        self.policy = policy


def match_constraint(field: str, value: str, constraints: list):
    for c in constraints:
        if field == c.field:
            if c.c_type == ConstraintType.INT.value:
                for interval in c.value:
                    try:
                        if interval[0] <= int(value) <= interval[1]:
                            return True
                    except ValueError:
                        return False
            elif c.c_type == ConstraintType.STR.value:
                if value in c.value:
                    return True
                else:
                    return False
            elif c.c_type == ConstraintType.TIME.value:
                continue
    return False

def match_packet(packet, mapping_entry):
    if packet.subject != mapping_entry.subject:
        return False

    for data in packet.content:
        if len(data) > 1:
            if len(mapping_entry.constraints)>0 and not match_constraint(data[0], data[1], mapping_entry.constraints):
                return False
        else:
            return False

    return True


class ConstraintMapping:
    def __init__(self):
        self.mapping = LockDictionary()

    def add_mapping(self, mark: str, entry: MappingEntry):
        self.mapping.set(mark, entry)

    def del_mapping(self, mark: str):
        self.mapping.delete(mark)

    def get_mapping(self, mark: str):
        return self.mapping.get(mark)

    def decision(self, packet):
        mapping_entry = self.mapping.get(packet.mark)
        if match_packet(packet, mapping_entry):
            print("Match!")
            return mapping_entry.policy
        else:
            print("No match!")
            return Policy.DEFAULT.value
