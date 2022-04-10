import ipaddress
import json

from client.member import Member
from utils.constant import *


def parse_member(name: str, src: str, m_type: MemberType = MemberType.DEVICE):
    if not name:
        raise ValueError("Error: You must specify a name.")

    ip = None
    n_ip = False
    port = None
    n_port = False

    if src:
        split = src.split(":")

        if len(split) > 1:
            port_part = split[1]
        else:
            port_part = None

        if split[0][0] == "n":
            ipaddress.IPv4Network(split[0][1:])
            ip = split[0][1:]
            n_ip = True
        else:
            ipaddress.IPv4Network(split[0])
            ip = split[0]

        if port_part:
            if port_part[0] == "n":
                port = int(port_part[1:])
                n_port = True
            else:
                port = int(port_part)

    if isinstance(port, int) and port > 65535:
        raise ValueError("Error: Port value must be between 0 and 65535.")

    return Member(name, ip, n_ip, port, n_port, m_type)


class JsonParser:
    def __init__(self, handlers, path: str):
        self.handlers = handlers
        self.path = path
        self.json = None
        self.parsed_labels = {}
        self.parsed_fields = {}
        self.parsed_relations = {}

    def __str__(self):
        result = f"Labels: {str(self.parsed_labels)}\n"
        result += f"Fields: {str(self.parsed_fields)}"
        return result

    def parse_json(self):
        try:
            self.json = json.load(open(self.path))
            self.parse_labels()
            self.parse_fields()
            self.parse_relations()
        except KeyError as err:
            return str(err)
        except ValueError as err:
            return str(err)
        except FileNotFoundError:
            return f"Error: File {self.path} not found."

    def parse_labels(self):
        label_dic = self.json["labels"]
        for key in label_dic.keys():
            try:
                value = label_dic[key]["value"]
            except KeyError:
                raise KeyError("Error: A label must contain a value.")
            if isinstance(value, int):
                self.parsed_labels[key] = {"type": "int", "value": value}
            elif isinstance(value, list):
                if len(value) != 2:
                    raise ValueError("Error: Int interval must contain two elements.")
                if not isinstance(value[0], int) or not isinstance(value[1], int):
                    raise ValueError("Error: Int value must be an integer.")
                self.parsed_labels[key] = {"type": "int", "value": value}
            else:
                raise ValueError("Error: Int value must be single or an interval.")

    def parse_fields(self):
        field_dic = self.json["fields"]
        for key in field_dic.keys():
            f_type = field_dic[key]
            field_types = set(item.value for item in FieldType)
            if f_type not in field_types:
                raise ValueError("Error: Wrong field type.")
            self.parsed_fields[key] = f_type

    def parse_members(self):
        pass

    def parse_relations(self):
        relations_list = self.json["relations"]
        for relation in relations_list:
            try:
                broker = parse_member("dev", relation["broker"], MemberType.BROKER.value)
                publisher = parse_member("dev", relation["publisher"], MemberType.PUB.value)
                subscriber = parse_member("dev", relation["subscriber"], MemberType.SUB.value)
            except KeyError as err:
                if err.args[0] in ["publisher", "subscriber"]:
                    return f"Error: You must specify a {err.args[0]}"
            except ipaddress.AddressValueError:
                return "Error: Incorrect ip format, correct format is IP{/BITMASK}."
            except ValueError as err:
                return str(err)
