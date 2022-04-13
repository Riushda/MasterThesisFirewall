import json

from client.constraint import Constraint
from client.member import Member
from client.utils import parse_member
from utils.constant import *


class JsonParser:
    def __init__(self, path: str):
        self.path = path
        self.json = None
        self.parsed_labels = {}
        self.converted_labels = {}
        self.parsed_members = {}
        self.parsed_relations = {}
        self.parsed_triggers = {}

        self.parse_json()

    def __str__(self):
        result = f"Labels: {str(self.parsed_labels)}\n\n"
        result += f"Converted labels: {str(self.converted_labels)}\n\n"
        result += "Members: "
        for key, value in self.parsed_members.items():
            result += f"[{key}: {value}]"
        result += "\n\n"
        result += "Relations: "
        result += str(list(self.parsed_relations.keys()))
        return result

    def parse_json(self):
        try:
            self.json = json.load(open(self.path))
            self.parse_label()
            self.parse_member()
            self.parse_relation()
        except FileNotFoundError:
            return f"Error: File {self.path} not found."
        except Exception as err:
            print(err.args[0])
            return err.args[0]
        return "Input parsed!"

    def parse_label(self):
        try:
            label_dic = self.json["label"]
        except KeyError:
            return
        for key in label_dic.keys():
            converted_label = {}
            try:
                value = label_dic[key][0]
                label = label_dic[key][1]
            except KeyError:
                raise KeyError("Error: Wrong categorization format.")
            int_v = []
            if len(value) != len(label) + 1:
                raise ValueError("Error: Wrong categorization format.")
            for v in value:
                try:
                    int_v.append(float(v))
                except ValueError:
                    raise ValueError("Error: Wrong categorization format.")
            for i in range(len(label)):
                if not isinstance(label[i], str):
                    raise ValueError("Error: Wrong categorization format.")
                converted_label[label[i]] = [int_v[i], int_v[i + 1]]
            self.converted_labels[key] = converted_label
            self.parsed_labels[key] = label_dic[key]

    def parse_member(self):
        try:
            member_dict = self.json["member"]
        except KeyError:
            return

        for key in member_dict.keys():
            field = None
            try:
                src = member_dict[key]["src"]
            except KeyError as err:
                raise KeyError(f"Error: A member must contain {err.args[0]}.")

            try:
                field = member_dict[key]["field"]
                if not isinstance(field, dict):
                    raise ValueError("Error: Field must be a dictionary.")
            except KeyError:
                pass

            if field:
                for k, f in field.items():
                    try:
                        f_type = f["type"]
                        if f_type not in [e.value for e in FieldType]:
                            raise ValueError("Error: Unknown field type.")
                    except KeyError:
                        raise KeyError("Error: A field must contain a type.")

                    if f_type == FieldType.INT.value:
                        try:
                            label = f["label"]
                        except KeyError:
                            raise KeyError("Error: A int field must be defined with a label.")
                        if label not in self.parsed_labels:
                            raise ValueError("Error: A label must be defined before using it.")
                    elif f_type == FieldType.STR.value:
                        try:
                            value = f["value"]
                        except KeyError:
                            raise KeyError("Error: A str field must be defined with a value.")
                        if not isinstance(value, list):
                            raise KeyError("Error: A str field value must be a list.")
                        for v in value:
                            if not isinstance(v, str):
                                raise KeyError("Error: A str field value must only contain strings.")

            parsed_member = parse_member(src=src, field=field)

            self.parsed_members[key] = parsed_member

    def parse_constraint(self, publisher: Member, constraints: list):
        constraint_list = []
        fields = []

        pub_fields = publisher.field

        for constraint in constraints:

            try:
                field = constraint["field"]
                value = constraint["value"]
            except KeyError:
                raise KeyError("Error: A constraint must contain a field and a value.")

            try:
                f_type = pub_fields[field]["type"]
            except KeyError:
                raise KeyError("Error: The publisher must contain the constrained field.")

            if f_type == FieldType.INT.value:
                label = pub_fields[field]["label"]
                value_list = []
                for v in value:
                    try:
                        converted_value = self.converted_labels[label][v]
                    except KeyError:
                        raise KeyError("Error: Invalid value specified for int constraint.")
                    value_list.append(converted_value)
                constraint_list.append(Constraint(ConstraintType(f_type), field, value_list))

            elif f_type == FieldType.STR.value:
                field_value = pub_fields[field]["value"]
                for v in value:
                    if v not in field_value:
                        raise ValueError("Error: Invalid value specified for str constraint.")
                constraint_list.append(Constraint(ConstraintType(f_type), field, value))

            if field not in fields:
                fields.append(field)
            else:
                raise ValueError(f"Error: Please merge constraints using the same field.")

        return constraint_list

    def parse_trigger(self, triggers):
        for trigger in triggers:
            try:
                condition = trigger["condition"]
                action = trigger["action"]
            except KeyError:
                raise KeyError("Error: A trigger must contain a condition and an action.")

            for name, member in condition.items():
                pass

    def parse_relation(self):
        try:
            relations_list = self.json["relation"]
        except KeyError:
            return

        for name, relation in relations_list.items():
            try:
                subject = relation["subject"]
                publisher_key = relation["publisher"]
                subscriber_key = relation["subscriber"]
            except KeyError as err:
                raise KeyError(f"Error: A relation must contain a {err.args[0]}.")

            broker = None

            try:
                broker_str = relation["broker"]
                if broker_str in self.parsed_members:
                    broker = self.parsed_members[broker_str]
                else:
                    raise ValueError("Error: Unknown member.")
            except KeyError:
                pass

            if publisher_key and subscriber_key in self.parsed_members:
                publisher = self.parsed_members[publisher_key]
                subscriber = self.parsed_members[subscriber_key]
            else:
                raise ValueError("Error: Unknown member.")

            constraints = None

            try:
                constraints = relation["constraints"]
            except KeyError:
                pass

            if constraints:
                constraints = self.parse_constraint(publisher, constraints)

            self.parsed_relations[name] = {"subject": subject, "broker": broker, "publisher": publisher,
                                           "subscriber": subscriber,
                                           "constraints": constraints}
