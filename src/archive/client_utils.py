from utils.constant import *


def parse_int_interval(value):
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


def schedule_job(api, code, relation):
    match code:
        case Code.ENABLE_RELATION:
            api.enable_rule(relation.first.handle)
            if relation.second:
                api.enable_rule(relation.second.handle)
        case Code.DISABLE_RELATION:
            api.disable_rule(relation.first.handle)
            if relation.second:
                api.disable_rule(relation.second.handle)
