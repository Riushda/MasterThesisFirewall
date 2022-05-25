"""
The parser is responsible for parsing the input file and returning parsing errors.
"""

import json

from client.relation import Constraint, Field, Member, parse_member
from client.utils import parse_time_interval, check_overlapping, invert_time_intervals
from client.constant import *


class Parser:
    def __init__(self, path: str):
        self.path = path
        self.json = None
        self.parsed_categorization = {}
        self.converted_categorization = {}
        self.parsed_members = {}
        self.parsed_relations = {}
        self.parsed_triggers = []
        self.parsed_inferences = []
        self.parsed_inconsistencies = []
        self.parsed_time_intervals = {}
        self.err = None

        self.parse_json()

    def __str__(self):
        result = f"Categorization: {self.parsed_categorization}\n\n"
        result += f"Converted categorization: {self.converted_categorization}\n\n"
        result += "Members: "
        for key, value in self.parsed_members.items():
            result += f"[{key}: {value}]"
        result += "\n\n"
        result += "Relations: "
        result += str(list(self.parsed_relations.keys()))
        result += "\n\n"
        result += f"Inferences: {self.parsed_inferences}"
        result += "\n\n"
        result += f"Inconsistencies: {self.parsed_inconsistencies}"
        result += "\n"
        return result

    def parse_json(self):
        try:
            self.json = json.load(open(self.path))
            self.parse_categorization()
            self.parse_member()
            self.parse_relation()
            self.parse_trigger()
            self.parse_inference()
            self.parse_inconsistency()
        except FileNotFoundError:
            self.err = f"Error: File {self.path} not found."
            return
        except Exception as err:
            self.err = err.args[0]
            return

    def parse_categorization(self):
        try:
            categorization_dic = self.json["categorization"]
        except KeyError:
            return

        for categorization_key, category in categorization_dic.items():
            converted_categorization = {}

            try:
                c_type = category["type"]
                category = category["value"]
            except KeyError:
                raise KeyError("Error in categorization parsing: A categorization must contain a type and a value.")

            if c_type == FieldType.DEC.value:
                try:
                    intervals = category[0]
                    labels = category[1]
                except KeyError:
                    raise KeyError(
                        "Error in categorization parsing: A categorization must contain intervals and labels.")

                int_value = []
                if len(intervals) != len(labels) + 1:
                    raise ValueError("Error in categorization parsing: Wrong categorization format.")
                if len(intervals) < 2:
                    raise ValueError("Error in categorization parsing: Wrong categorization format.")
                for i in range(len(intervals)):
                    try:
                        int_value.append(float(intervals[i]))
                        if (i == 0 and intervals[i] == "inf") or (i == len(intervals) - 1 and intervals[i] == "-inf"):
                            raise ValueError
                    except ValueError:
                        raise ValueError("Error in categorization parsing: Wrong categorization format.")

                for i in range(len(labels)):
                    if not isinstance(labels[i], str):
                        raise ValueError("Error in categorization parsing: Wrong categorization format.")
                    converted_categorization[labels[i]] = [int_value[i], int_value[i + 1]]
                self.converted_categorization[categorization_key] = converted_categorization
                self.parsed_categorization[categorization_key] = categorization_dic[categorization_key]["value"]
            elif c_type == TriggerType.TIME.value:
                parse_time_interval(category)
                self.parsed_time_intervals[categorization_key] = category

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

                    if f_type == FieldType.DEC.value:
                        if value not in self.parsed_categorization:
                            raise ValueError("Error in field parsing: A categorization must be defined before usage.")
                        if init_value not in self.converted_categorization[value].keys():
                            raise ValueError("Error in field parsing: Int field initial value unknown.")
                    elif f_type == FieldType.STR.value:
                        if not isinstance(value, list):
                            raise KeyError("Error in field parsing: A string field value must be a list.")
                        for v in value:
                            if not isinstance(v, str):
                                raise KeyError(
                                    "Error in field parsing: A string field value must only contain strings.")
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

            if f_type == FieldType.DEC:
                category = pub_fields[field_key].value
                category_list = []
                for v in value:
                    try:
                        converted_value = self.converted_categorization[category][v]
                    except KeyError:
                        raise KeyError("Error in constraint parsing: Invalid value specified for decimal constraint.")
                    category_list.append(converted_value)
                value = category_list

            elif f_type == FieldType.STR:
                field_value = pub_fields[field_key].value
                for v in value:
                    if v not in field_value:
                        raise ValueError("Error in constraint parsing: Invalid value specified for string constraint.")

            constraint_list.append(Constraint(f_type, field_key, value))

            if field_key not in fields:
                fields.append(field_key)
            else:
                raise ValueError(f"Error in constraint parsing: Merge constraints using the same field.")

        return constraint_list

    def check_conditions(self, conditions, parsing):
        for member_key, conditioned_fields in conditions.items():
            if member_key not in self.parsed_members:
                raise KeyError(f"Error in {parsing} parsing: A(n) {parsing} must contain valid member(s).")
            found_member = self.parsed_members[member_key]
            member_fields = found_member.fields

            for field_key, field_value in conditioned_fields.items():
                if field_key in member_fields:
                    found_field = member_fields[field_key]
                else:
                    raise KeyError(f"Error in {parsing} parsing: Unknown field.")

                value = found_field.value

                if found_field.f_type == FieldType.DEC:
                    if field_value not in self.converted_categorization[value]:
                        raise ValueError(f"Error in {parsing} parsing: Wrong value for decimal field.")
                elif found_field.f_type == FieldType.STR:
                    if not isinstance(field_value, str):
                        raise ValueError(f"Error in {parsing} parsing: Wrong value for string field.")
                    if field_value not in found_field.value:
                        raise ValueError(f"Error in {parsing} parsing: Wrong value for string field.")

    def check_time_intervals(self, intervals):
        result = []
        for interval in intervals:
            if isinstance(interval, list):
                parse_time_interval(interval)
                result.append(interval)
            elif isinstance(interval, str):
                if interval in self.parsed_time_intervals:
                    result.append(self.parsed_time_intervals[interval])
                else:
                    raise ValueError("Error: A time interval must be defined before using it.")
            else:
                raise ValueError("Error: Unknown time value.")

        check_overlapping(result)
        return result

    def parse_trigger(self):
        try:
            triggers = self.json["trigger"]
        except KeyError:
            return

        for trigger in triggers:
            t_type = None
            try:
                conditions = trigger["condition"]
                action = trigger["action"]
            except KeyError:
                raise KeyError("Error in trigger parsing: A trigger must contain a condition and an action.")

            # TODO relation list inside trigger
            relation = None
            if Action.ENABLE.value in action:
                if action[Action.ENABLE.value] not in self.parsed_relations:
                    raise ValueError("Error in trigger parsing: Unknown action.")
                relation = action[Action.ENABLE.value]
                action = Action.ENABLE
            elif Action.DISABLE.value in action:
                if action[Action.DISABLE.value] not in self.parsed_relations:
                    raise ValueError("Error in trigger parsing: Unknown action.")
                relation = action[Action.DISABLE.value]
                action = Action.DISABLE

            try:
                conditions = conditions["field"]
                t_type = TriggerType.FIELD
            except KeyError:
                pass

            try:
                conditions = conditions["time"]
                t_type = TriggerType.TIME
            except KeyError:
                pass

            if t_type == TriggerType.FIELD:
                self.check_conditions(conditions, "trigger")
                trigger["condition"] = trigger["condition"]["field"]
                self.parsed_triggers.append(trigger)
            elif t_type == TriggerType.TIME:
                intervals = self.check_time_intervals(conditions)
                if action == Action.ENABLE:
                    self.parsed_relations[relation]["time_intervals"] = intervals
                elif action == Action.DISABLE:
                    # Invert the array of intervals
                    self.parsed_relations[relation]["time_intervals"] = invert_time_intervals(intervals)

    def parse_inference(self):
        try:
            inference_list = self.json["inference"]
        except KeyError:
            return

        for inference in inference_list:
            try:
                condition = inference["condition"]
                implications = inference["implication"]
            except KeyError:
                raise KeyError("Error in inference parsing: An inference must contain a condition and an implication.")

            if (len(condition.keys())) != 1:
                raise KeyError("Error in inference parsing: A condition must contain a single member field.")

            self.check_conditions(condition, "inference")
            self.check_conditions(implications, "inference")
            self.parsed_inferences.append(inference)

    def parse_inconsistency(self):
        try:
            inconsistency_list = self.json["inconsistency"]
        except KeyError:
            return

        for inconsistency in inconsistency_list:
            self.check_conditions(inconsistency, "inconsistency")
            self.parsed_inconsistencies.append(inconsistency)

    def parse_relation(self):
        try:
            relations_dic = self.json["relation"]
        except KeyError:
            return

        for relation_key, relation in relations_dic.items():
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
                                                   "constraints": constraints,
                                                   "time_intervals": []}
