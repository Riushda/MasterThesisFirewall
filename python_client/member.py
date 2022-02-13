import ipaddress
from constant import *


class Member():
    def __init__(self, name, ip=0, bitmask=0, port=0, n_port=0, type: M_TYPE = M_TYPE.PUB.value):
        self.name = name
        self.type = type
        self.ip = ip
        self.bitmask = bitmask
        self.port = port
        self.n_port = n_port

    def __str__(self):
        if(self.n_port == 0):
            return f"{ipaddress.IPv4Address(self.ip)}/{self.bitmask}:{self.port}"
        else:
            return f"{ipaddress.IPv4Address(self.ip)}/{self.bitmask}:!{self.port}"

    def to_bytes(self):
        buffer = bytearray()
        buffer += self.ip.to_bytes(4, 'big')
        buffer += self.bitmask.to_bytes(1, 'little')
        buffer += self.port.to_bytes(2, 'big')
        buffer += self.n_port.to_bytes(1, 'little')
        return buffer


def parse_member(name, str_ip, str_port, type):

    ip = 0
    bitmask = 32
    port = 0
    n_port = 0

    if(name == "/"):
        return "Error: This name is reserved, please enter another."

    split = str_ip.split("/")
    if(len(split) > 2):
        return "Error: Incorrect ip format, correct format is IP{/BITMASK}."

    if(len(split) > 1):
        bitmask = int(split[1])
        if(bitmask > 32):
            return "Error: Bitmask max value is 32."

    if(split[0] != "any"):
        try:
            ip = int(ipaddress.IPv4Address(split[0]))
        except(ipaddress.AddressValueError):
            return "Error: Incorrect ip format, correct format is IP{/BITMASK}."
    else:
        bitmask = 0

    if(str_port != "any"):
        if(str_port[0][0] == "-"):
            port = int(str_port[1:])
            n_port = 1
        else:
            port = int(str_port)

    if(port > 65535):
        return "Error: Port max value is 65535."

    return Member(name, ip, bitmask, port, n_port, type)
