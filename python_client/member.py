import ipaddress
from constant import *


class Member():
    def __init__(self, name: str, ip: str = None, n_ip: bool = False, port: str = None, n_port: bool = False, m_type: M_TYPE = M_TYPE.PUB.value):
        self.name = name
        self.m_type = m_type
        self.ip = ip
        self.n_ip = n_ip
        self.port = port
        self.n_port = n_port

    def __str__(self):
        string = ""

        if(self.n_ip):
            string += "!"
        if(self.ip):
            string += self.ip + ":"
        else:
            string += "*:"

        if(self.n_port):
            string += "!"
        if(self.port):
            string += str(self.port)
        else:
            string += "*"

        return string


def parse_member(name: str, str_ip: str, str_port: str, m_type: M_TYPE):

    if(not name):
        return "Error: You must specify a name."

    ip = None
    n_ip = False
    port = None
    n_port = False

    if(str_ip):
        split = str_ip.split("/")
        if(len(split) > 2):
            return "Error: Incorrect ip format, correct format is IP{/BITMASK}."

        if(len(split) > 1):
            bitmask = int(split[1])
            if(bitmask > 32):
                return "Error: Bitmask max value is 32."

        try:
            if(str_ip[0] == "n"):
                ipaddress.IPv4Address(split[0][1:])
                ip = str_ip[1:]
                n_ip = True
            else:
                ipaddress.IPv4Address(split[0])
                ip = str_ip
        except(ipaddress.AddressValueError):
            return "Error: Incorrect ip format, correct format is IP{/BITMASK}."

    if(str_port):
        if(str_port[0] == "n"):
            port = int(str_port[1:])
            n_port = True
        else:
            port = int(str_port)

    if(isinstance(port, int) and port > 65535):
        return "Error: Port max value is 65535."

    return Member(name, ip, n_ip, port, n_port, m_type)
