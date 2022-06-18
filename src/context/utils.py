"""
This class contains some utility functions used by the classes of this package.
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
        subject = relation.subject
        if relation.second:
            marks = [relation.first[0].mark, relation.second[0].mark]
        else:
            marks = [relation.first[0].mark]

        for interval in relation.time_intervals:
            for mark in marks:
                job = schedule.every().day.at(interval[0]).do(
                    constraint_mapping.enable_relation, mark, subject)
                schedule_thread.jobs.append(job)

                job = schedule.every().day.at(interval[1]).do(
                    constraint_mapping.disable_relation, mark, subject)
                schedule_thread.jobs.append(job)


def get_transition_trigger(key, value):
    return key + "=" + str(value)
