def get_device_name(ip, members):
    for device_key, device in members.items():
        if device.ip == ip:
            return device_key

    return None


def get_device(field):
    key_list = field.split(".")
    return key_list[0]


def is_float(string):
    try:
        float(string)
    except ValueError:
        return False
    return True


def flatten_state(state):
    flattened = {}
    for device in state:
        for field in state[device]:
            flat_field = device + "." + field
            flattened[flat_field] = state[device][field]

    return flattened


def add_relations_jobs(context_input, schedule_thread):
    schedule = schedule_thread.schedule
    handler = context_input.handler
    relations = context_input.relations
    for relation_key, relation in relations.items():
        for interval in relation.time_intervals:
            job = schedule.every().day.at(interval[0]).do(
                handler.enable_relation, relation_key)
            schedule_thread.jobs.append(job)

            job = schedule.every().day.at(interval[1]).do(
                handler.disable_relation, relation_key)
            schedule_thread.jobs.append(job)


def get_transition_trigger(key, value):
    return key + "=" + str(value)
