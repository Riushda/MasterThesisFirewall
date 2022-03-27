import ipaddress

from utils.constant import *


class Member:
    def __init__(self, name: str, ip: str = None, n_ip: bool = False, port: int = None, n_port: bool = False,
                 m_type: MemberType = MemberType.PUB.value):
        self.name = name
        self.m_type = m_type
        self.ip = ip
        self.n_ip = n_ip
        self.port = port
        self.n_port = n_port

    def __str__(self):
        string = ""

        if self.n_ip:
            string += "!"
        if self.ip:
            string += self.ip + ":"
        else:
            string += "*:"

        if self.n_port:
            string += "!"
        if self.port:
            string += str(self.port)
        else:
            string += "*"

        return string


def parse_member(name: str, src: str, m_type: MemberType = MemberType.DEVICE):
    if not name:
        return "Error: You must specify a name."

    ip = None
    n_ip = False
    port = None
    n_port = False

    if src:
        split = src.split(":")
        ip_part = split[0].split("/")

        if len(split) > 1:
            port_part = split[1]
        else:
            port_part = None

        if len(ip_part) > 2:
            return "Error: Incorrect ip format, correct format is IP{/BITMASK}."

        if len(ip_part) > 1:
            bitmask = int(ip_part[1])
            if bitmask > 32:
                return "Error: Bitmask max value is 32."

        try:
            if ip_part[0][0] == "n":
                ipaddress.IPv4Address(ip_part[0][1:])
                ip = split[0][1:]
                n_ip = True
            else:
                ipaddress.IPv4Address(ip_part[0])
                ip = split[0]
        except ipaddress.AddressValueError:
            return "Error: Incorrect ip format, correct format is IP{/BITMASK}."

        if port_part:
            if port_part[0] == "n":
                port = int(port_part[1:])
                n_port = True
            else:
                port = int(port_part)

    if isinstance(port, int) and port > 65535:
        return "Error: Port max value is 65535."

    return Member(name, ip, n_ip, port, n_port, m_type)
