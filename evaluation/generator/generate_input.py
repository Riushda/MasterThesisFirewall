import ipaddress
import json
import random

from constant import *


def integer_to_ip(int_ip):
    return ipaddress.ip_address(int_ip).__str__()


def generate_fields(n_fields, n_values):
    field_dict = {}
    for i in range(0, n_fields):
        field_dict[str(i)] = {
            "type": "string",
            "value": [],
            "init": "0"
        }
        for j in range(0, n_values):
            field_dict[str(i)]["value"].append(str(j))
    return field_dict


class MemberGenerator:
    def __init__(self, n_members, n_fields, n_values):
        self.n_members = n_members
        self.n_fields = n_fields
        self.n_values = max(1, n_values)
        self.members = {}

    def generate_ip(self):
        int_ip = random.randint(0, MAX_IP)
        string_ip = integer_to_ip(int_ip)
        while string_ip in INVALID_IPS or string_ip in self.members:
            int_ip = random.randint(0, MAX_IP)
            string_ip = integer_to_ip(int_ip)
        return string_ip

    def generate(self):
        for i in range(0, self.n_members):
            string_ip = self.generate_ip()
            self.members[string_ip] = {"src": string_ip}
            if self.n_fields > 0:
                fields = generate_fields(self.n_fields, self.n_values)
                self.members[string_ip]["field"] = fields
        return self.members


class RelationGenerator:
    def __init__(self, m, n_relations):
        self.members = m
        self.n_relations = n_relations
        self.relations = {}

    def generate(self):
        count = 0
        try:
            for i in self.members.keys():
                for j in self.members.keys():
                    if i != j:
                        new_relation = {"subject": i + j, "publisher": i, "broker": "broker", "subscriber": j}
                        self.relations[i + j] = new_relation
                        count += 1
                        if count == self.n_relations:
                            raise Exception
        except Exception:
            print("Relation limit reached!")
            pass
        return self.relations




if __name__ == "__main__":
    members = MemberGenerator(N_MEMBERS, N_FIELDS, N_VALUES).generate()
    relations = RelationGenerator(members, N_RELATIONS).generate()
    members["broker"] = {"src": "192.168.33.11;1883"}
    members["subscriber"] = {"src": "192.168.33.13"}
    members["publisher"] = json.load(open("publisher.json"))
    relation = json.load(open("relation.json"))
    relations["relation"] = relation
    categorization = json.load(open("categorization.json"))
    new_input = {"categorization": categorization, "member": members, "relation": relations}
    json_object = json.dumps(new_input, indent=4)
    with open('../../src/test.json', 'w') as f:
        f.write(json_object)
