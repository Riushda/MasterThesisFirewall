"""
This class contains some utilities function used by many classes in this package.
"""


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
    constraint_mapping = context_input.relation_mapping
    relations = context_input.relations
    for relation_key, relation in relations.items():
        mark = relation.mark
        subject = relation.subject
        for interval in relation.time_intervals:
            job = schedule.every().day.at(interval[0]).do(
                constraint_mapping.enable_relation, mark, subject)
            schedule_thread.jobs.append(job)

            job = schedule.every().day.at(interval[1]).do(
                constraint_mapping.disable_relation, mark, subject)
            schedule_thread.jobs.append(job)


def get_transition_trigger(key, value):
    return key + "=" + str(value)
