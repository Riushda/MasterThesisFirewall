import json

from client.constraint import Constraint
from client.field import Field
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
        self.parsed_triggers = []

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
            self.parse_trigger()
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

        for label_key, label in label_dic.items():
            converted_label = {}
            try:
                values = label[0]
                categories = label[1]
            except KeyError:
                raise KeyError("Error in label parsing: Categorization must contain values and categories.")

            int_value = []
            if len(values) != len(categories) + 1:
                raise ValueError("Error in label parsing: Wrong categorization format.")
            for value in values:
                try:
                    int_value.append(float(value))
                except ValueError:
                    raise ValueError("Error in label parsing: Wrong categorization format.")
            for i in range(len(categories)):
                if not isinstance(categories[i], str):
                    raise ValueError("Error in label parsing: Wrong categorization format.")
                converted_label[categories[i]] = [int_value[i], int_value[i + 1]]
            self.converted_labels[label_key] = converted_label
            self.parsed_labels[label_key] = label_dic[label_key]

    def parse_member(self):
        try:
            member_dict = self.json["member"]
        except KeyError:
            return

        for member_key, member in member_dict.items():
            try:
                src = member["src"]
            except KeyError as err:
                raise KeyError(f"Error in member parsing: A member must contain {err.args[0]}.")

            json_field = None

            try:
                json_field = member["field"]
            except KeyError:
                pass

            parsed_fields = {}

            if json_field:
                for field_key, field in json_field.items():
                    try:
                        f_type = field["type"]
                        value = field["value"]
                        init_value = field["init"]
                        if f_type not in [e.value for e in FieldType]:
                            raise ValueError("Error in field parsing: Unknown field type.")
                    except KeyError as err:
                        raise KeyError(f"Error in field parsing: A field must contain a {err.args[0]}.")

                    if f_type == FieldType.INT.value:
                        if value not in self.parsed_labels:
                            raise ValueError("Error in field parsing: A label must be defined before usage.")
                        if init_value not in self.converted_labels[value].keys():
                            raise ValueError("Error in field parsing: Int field initial value unknown.")
                    elif f_type == FieldType.STR.value:
                        if not isinstance(value, list):
                            raise KeyError("Error in field parsing: A str field value must be a list.")
                        for v in value:
                            if not isinstance(v, str):
                                raise KeyError("Error in field parsing: A str field value must only contain strings.")
                        if init_value not in value:
                            raise ValueError("Error in field parsing: Str field initial value unknown.")

                    parsed_fields[field_key] = Field(FieldType(f_type), value, init_value)

            parsed_member = parse_member(src=src, field=parsed_fields)
            self.parsed_members[member_key] = parsed_member

    def parse_constraint(self, publisher: Member, constraints: list):
        constraint_list = []
        fields = []

        pub_fields = publisher.fields

        for constraint in constraints:

            try:
                field_key = constraint["field"]
                value = constraint["value"]
            except KeyError:
                raise KeyError("Error in constraint parsing: A constraint must contain a field and a value.")

            try:
                f_type = pub_fields[field_key].f_type
            except KeyError:
                raise KeyError("Error in constraint parsing: The publisher must contain the constrained field.")

            if f_type == FieldType.INT:
                label = pub_fields[field_key].value
                category_list = []
                for v in value:
                    try:
                        converted_value = self.converted_labels[label][v]
                    except KeyError:
                        raise KeyError("Error in constraint parsing: Invalid value specified for int constraint.")
                    category_list.append(converted_value)
                value = category_list

            elif f_type == FieldType.STR:
                field_value = pub_fields[field_key].value
                for v in value:
                    if v not in field_value:
                        raise ValueError("Error in constraint parsing: Invalid value specified for str constraint.")

            constraint_list.append(Constraint(f_type, field_key, value))

            if field_key not in fields:
                fields.append(field_key)
            else:
                raise ValueError(f"Error in constraint parsing: Merge constraints using the same field.")

        return constraint_list

    def parse_trigger(self):
        try:
            triggers = self.json["trigger"]
        except KeyError:
            return

        for trigger in triggers:
            try:
                condition = trigger["condition"]
                action = trigger["action"]
            except KeyError:
                raise KeyError("Error in trigger parsing: A trigger must contain a condition and an action.")

            for member_key, conditioned_fields in condition.items():
                if member_key not in self.parsed_members:
                    raise KeyError("Error in trigger parsing: A trigger must contain valid member(s).")
                found_member = self.parsed_members[member_key]
                member_fields = found_member.fields

                for field_key, field_value in conditioned_fields.items():
                    if field_key in member_fields:
                        found_field = member_fields[field_key]
                    else:
                        raise KeyError("Error in trigger parsing: Unknown field.")

                    value = found_field.value

                    if found_field.f_type == FieldType.INT:
                        if field_value not in self.converted_labels[value]:
                            raise ValueError("Error in trigger parsing: Wrong value for int field.")
                    elif found_field.f_type == FieldType.STR:
                        if not isinstance(field_value, str):
                            raise ValueError("Error in trigger parsing: Wrong value for str field.")
                        if field_value not in found_field.value:
                            raise ValueError("Error in trigger parsing: Wrong value for str field.")

            if Action.ENABLE.value in action:
                if action[Action.ENABLE.value] not in self.parsed_relations:
                    raise ValueError("Error in trigger parsing: Unknown action.")

            if Action.DISABLE.value in action:
                if action[Action.DISABLE.value] not in self.parsed_relations:
                    raise ValueError("Error in trigger parsing: Unknown action.")

            self.parsed_triggers.append(trigger)

    def parse_relation(self):
        try:
            relations_list = self.json["relation"]
        except KeyError:
            return

        for relation_key, relation in relations_list.items():
            try:
                subject = relation["subject"]
                publisher_key = relation["publisher"]
                subscriber_key = relation["subscriber"]
            except KeyError as err:
                raise KeyError(f"Error in relation parsing: A relation must contain a {err.args[0]}.")

            broker = None

            try:
                broker_str = relation["broker"]
                if broker_str in self.parsed_members:
                    broker = self.parsed_members[broker_str]
                else:
                    raise ValueError("Error in relation parsing: Unknown member.")
            except KeyError:
                pass

            if publisher_key and subscriber_key in self.parsed_members:
                publisher = self.parsed_members[publisher_key]
                subscriber = self.parsed_members[subscriber_key]
            else:
                raise ValueError("Error in relation parsing: Unknown member.")

            for m1 in [broker, publisher, subscriber]:
                for m2 in [broker, publisher, subscriber]:
                    if not broker:
                        continue
                    if m1.is_ip6 ^ m2.is_ip6:
                        raise ValueError("Error in relation parsing: All members must have the same address family.")

            constraints = None

            try:
                constraints = relation["constraints"]
            except KeyError:
                pass

            if constraints:
                constraints = self.parse_constraint(publisher, constraints)

            self.parsed_relations[relation_key] = {"subject": subject, "broker": broker, "publisher": publisher,
                                                   "subscriber": subscriber,
                                                   "constraints": constraints}
