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
        buffer += self.port.to_bytes(2, 'little')
        buffer += self.n_port.to_bytes(1, 'little')
        return buffer


def create_member(ip, port):

    member = Member()

    split = ip.split("/")
    if(len(split) > 2):
        raise ValueError

    bitmask = 32
    if(len(split) > 1):
        bitmask = int(split[1])

    if(split[0] != "*"):
        member.ip = int(ipaddress.IPv4Address(
            split[0]))
        member.bitmask = bitmask  # .to_bytes(1, 'big')
    else:
        member.bitmask = 0

    if(port != "*"):
        if(port[0][0] == "-"):
            member.port = int(port[1:])
            member.n_port = 1
        else:
            member.port = int(port)

    return member


def parse_member(name, str_ip, str_port, type):

    ip = 0
    bitmask = 32
    port = 0
    n_port = 0

    if(name == "/"):
        print("Error: This name is reserved, please enter another.")
        return None

    split = str_ip.split("/")
    if(len(split) > 2):
        print("Error: Incorrect ip format, correct format is IP[/BITMASK].")
        return None

    if(len(split) > 1):
        bitmask = int(split[1])
        if(bitmask > 32):
            print("Error: Bitmask max value is 32.")
            return None

    if(split[0] != "*"):
        ip = int(ipaddress.IPv4Address(split[0]))
    else:
        bitmask = 0

    if(str_port != "*"):
        if(str_port[0][0] == "-"):
            port = int(str_port[1:])
            n_port = 1
        else:
            port = int(str_port)

    if(port > 65535):
        print("Error: Port max value is 65535.")
        return None

    return Member(name, ip, bitmask, port, n_port, type)
