from utils.constant import *

class Subject:
    def __init__(self, subject: str, constraints: list):
        self.subject = subject
        self.constraints = constraints
        self.enabled = True


class MappingEntry:
    def __init__(self, subject: Subject):
        self.subject_list = [subject]

    def add_subject(self, subject: Subject):
        self.subject_list.append(subject)


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
                return value in c.value
    return False

def match_packet(packet, mapping_entry):
    for subject in mapping_entry.subject_list:
        if packet.subject == subject.subject:
            if not subject.enabled:
                return False

            # No constraint on this relation
            if len(subject.constraints) == 0:
                return True

            for data in packet.content:
                if len(data) > 1:
                    if not match_constraint(data[0], data[1], subject.constraints):
                        return False
                else:
                    return False

            return True
    return False


class ConstraintMapping:
    def __init__(self):
        self.mapping = {}

    def add_mapping(self, mark: int, subject: Subject):
        if mark not in self.mapping:
            self.mapping[mark] = MappingEntry(subject)
        else:
            self.mapping[mark].add_subject(subject)

    def del_mapping(self, mark: int):
        del self.mapping[mark]

    def get_mapping(self, mark: int):
        return self.mapping[mark]

    def enable_mapping(self, mark: int, relation_subject: str):
        for subject in self.mapping[mark].subject_list:
            if subject.subject == relation_subject:
                subject.enabled = True

    def disable_mapping(self, mark: int, relation_subject: str):
        for subject in self.mapping[mark].subject_list:
            if subject.subject == relation_subject:
                subject.enabled = False

    def decision(self, packet):
        mapping_entry = self.mapping[packet.mark]
        if match_packet(packet, mapping_entry):
            print("Match!")
            return Policy.ACCEPT
        else:
            print("No match!")
            return Policy.DROP
