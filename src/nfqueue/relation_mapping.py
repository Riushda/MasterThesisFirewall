"""
This class defines the relation mapping used to match relations to their constraints
in order to complete the last step of the application layer matching. It is also
responsible for tracking the status of relations, whether they are enabled or disabled.
"""

from client.constant import *


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
    if packet.subject in mapping_entry.relations:
        relation = mapping_entry.relations[packet.subject]
        if not relation.enabled:
            return False

        # No constraint on this relation
        if not relation.constraints:
            return True

        for data in packet.content:
            if len(data) > 1:
                if not match_constraint(data[0], data[1], relation.constraints):
                    return False
            else:
                return False

        return True
    return False


class Relation:
    def __init__(self, subject: str, constraints: list):
        self.subject = subject
        self.constraints = constraints
        self.enabled = True


class Entry:
    def __init__(self, relation: Relation):
        self.relations = {relation.subject: relation}

    def add_relation(self, relation: Relation):
        self.relations[relation.subject] = relation


class RelationMapping:
    def __init__(self):
        self.mapping = {}

    def add_relation(self, mark: int, relation: Relation):
        if mark not in self.mapping:
            self.mapping[mark] = Entry(relation)
        else:
            self.mapping[mark].add_relation(relation)

    def del_relation(self, mark: int):
        del self.mapping[mark]

    def get_relation(self, mark: int):
        return self.mapping[mark]

    def enable_relation(self, mark: int, subject: str):
        self.mapping[mark].relations[subject].enabled = True

    def disable_relation(self, mark: int, subject: str):
        self.mapping[mark].relations[subject].enabled = False

    def decision(self, packet):
        mapping_entry = self.mapping[packet.mark]
        if match_packet(packet, mapping_entry):
            return Policy.ACCEPT
        else:
            return Policy.DROP
