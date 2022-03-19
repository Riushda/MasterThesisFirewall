from utils.constant import *


class Constraint:
    def __init__(self, c_type: MemberType, field: str = "", values=None):
        self.type = c_type
        self.field_len = len(field)
        self.field = field
        self.n_values = 0
        if values:
            self.n_values = len(values)
        self.values = values

    def __str__(self):
        return f"Type: {self.type} | Field: {self.field} | Values: {self.values}"


def parse_interval(value):
    if len(value) == 1:
        try:
            interval = [int(value[0]), int(value[0])]
        except ValueError:
            return f"Error: Wrong value for int, it must an integer."
    elif len(value) == 2:
        try:
            interval = [int(value[0]), int(value[1])]
        except ValueError:
            return f"Error: Wrong value for int, it must an integer."
    else:
        return f"Error: Wrong value for int, format is number or number-number."

    return interval


def parse_time_interval(value):
    if len(value) == 2:
        for x in range(0, 2):
            split = value[x].split(":")
            if len(split) != 2:
                return f"Error: Wrong value for time, format is xx:xx-xx:xx."
            try:
                if not (0 <= int(split[0]) < 24) or not (0 <= int(split[1]) < 60):
                    raise ValueError
            except ValueError:
                return f"Error: Wrong value for time, it must an integer. Max hour is 23 and max minute is 59."
    else:
        return f"Error: Wrong value for time, format is xx:xx-xx:xx."

    return [value[0], value[1]]


def parse_context(context):
    constraint_list = []
    names = []

    for c in context:

        split = c.split("/")
        if split[1] not in names:
            names.append(split[1])
        else:
            return f"Error: constraints names must be unique."

        match split[0]:
            case StringConstraint.SUBJECT.value:
                constraint = Constraint(
                    IntegerConstraint[split[0].upper()].value, split[1])
            case StringConstraint.INT.value:
                intervals = []
                for x in range(2, len(split)):
                    value = split[x].split("-")
                    interval = parse_interval(value)
                    if not isinstance(interval, list):
                        return interval
                    intervals.append(interval)
                constraint = Constraint(
                    IntegerConstraint[split[0].upper()].value, split[1], intervals)
            case StringConstraint.STR.value:
                values = []
                for x in range(2, len(split)):
                    value = split[x].split("-")
                    values.append([len(value[0]), value[0]])
                constraint = Constraint(
                    IntegerConstraint[split[0].upper()].value, split[1], values)
            case StringConstraint.TIME.value:
                intervals = []
                for x in range(1, len(split)):
                    value = split[x].split("-")
                    interval = parse_time_interval(value)
                    if not isinstance(interval, list):
                        return interval
                    intervals.append(interval)
                constraint = Constraint(
                    IntegerConstraint[split[0].upper()].value, "", intervals)
            case _:
                return f"Error: Wrong constraint type, possible values are {[e.value for e in StringConstraint]}."

        constraint_list.append(constraint)

    return constraint_list
