import ipaddress

from utils.constant import FieldType


class Member:
    def __init__(self, ip: str = None, port: int = None, fields=None, is_ip6: bool = False):
        self.ip = ip
        self.is_ip6 = is_ip6
        self.port = port
        if fields is None:
            self.fields = {}
        else:
            self.fields = fields

    def __str__(self):
        result = "source: "

        if self.ip:
            result += self.ip + ":"
        else:
            result += "*:"

        if self.port:
            result += str(self.port)
        else:
            result += "*"

        result += " | fields: "
        if self.fields:
            for field, content in self.fields.items():
                result += f"{content}"
        else:
            result += "none"

        return result


class Constraint:
    def __init__(self, f_type: FieldType, field: str, value: list):
        self.f_type = f_type
        self.field = field
        self.value = value

    def __str__(self):
        return f"type: {self.f_type.value} | field: {self.field} | value: {self.value}"


class Field:
    def __init__(self, f_type: FieldType, value, init: str):
        self.f_type = f_type
        self.value = value
        self.init = init


class Rule:
    def __init__(self, src: Member, dst: Member, handle: int):
        self.src = src
        self.dst = dst
        self.handle = handle

    def __str__(self):
        return f"{self.src} -> {self.dst}"


class Relation:
    def __init__(self, subject: str, mark: int, first: list, second: list = None, constraints: list = None,
                 time_intervals=None):
        if time_intervals is None:
            time_intervals = []
        self.subject = subject
        self.mark = mark
        self.first = first
        self.second = second
        self.constraints = constraints
        self.time_intervals = time_intervals

    def __str__(self):
        result = f"subject: {self.subject} | mark: {self.mark} | "
        constraint_str = ""
        for c in self.constraints:
            constraint_str += f"{c} ; "
        result += "rules: "
        if self.second:
            result += f"{self.first[0]} ~ {self.second[0]}"
        else:
            result += f"{self.first[0]}"
        result += f"\n constraints: {constraint_str}"
        return result


def parse_member(src: str, field: dict = None):
    ip = None
    port = None

    is_ip4 = False
    is_ip6 = False

    if src:
        split = src.split(";")

        if len(split) > 1:
            port_part = split[1]
        else:
            port_part = None

        try:
            ipaddress.IPv4Network(split[0])
            ip = split[0]
            is_ip4 = True
        except ipaddress.AddressValueError:
            pass
        except ValueError:
            raise ValueError("Error: Incorrect ip format, host bits set.")

        if not is_ip4:
            try:
                ipaddress.IPv6Network(split[0])
                ip = split[0]
                is_ip6 = True
            except ipaddress.AddressValueError:
                pass
            except ValueError:
                raise ValueError("Error: Incorrect ip format, host bits set.")

        if not (is_ip4 or is_ip6):
            raise ValueError("Error: Incorrect ip format, correct format is IP{/BITMASK}{;PORT}.")

        if port_part:
            try:
                port = int(port_part)
            except ValueError:
                raise ValueError("Error: Port value must an integer.")

            if not 0 <= port <= 65535:
                raise ValueError("Error: Port value must be between 0 and 65535.")

    return Member(ip=ip, port=port, fields=field, is_ip6=is_ip6)
