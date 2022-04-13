import ipaddress

from client.member import Member
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


def parse_member(src: str, field: dict = None):
    ip = None
    port = None

    if src:
        split = src.split(":")

        if len(split) > 1:
            port_part = split[1]
        else:
            port_part = None

        try:
            ipaddress.IPv4Network(split[0])
            ip = split[0]
        except ipaddress.AddressValueError:
            raise ValueError("Error: Incorrect ip format, correct format is IP{/BITMASK}.")

        if port_part:
            try:
                port = int(port_part)
            except ValueError:
                raise ValueError("Error: Port value must an integer.")

            if not 0 <= port <= 65535:
                raise ValueError("Error: Port value must be between 0 and 65535.")

    return Member(ip=ip, port=port, field=field)
