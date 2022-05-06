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
