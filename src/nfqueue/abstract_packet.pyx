import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6

from nfqueue.protocol_decoder import ProtocolDecoder

class AbstractPacket:

    def __init__(self):
        self.mark = None
        self.src = None
        self.dst = None
        self.sport = None
        self.dport = None
        self.proto = None
        self.header = None
        self.subject = None
        self.content = None

    def __str__(self) -> str:
        return "mark:" + str(self.mark) + " src:" + self.src + " dst:" + self.dst \
               + " sport:" + str(self.sport) + " dport:" + str(self.dport) \
               + "\n    proto:" + self.proto + " header:" + str(self.header) \
               + "\n    subject:" + str(self.subject) + " content:" + str(self.content) + "\n"

    def parse_network(self, packet):
        if packet.haslayer(IP):
            self.src = packet[IP].src
            self.dst = packet[IP].dst
        elif packet.haslayer(IPv6):
            self.src = packet[IPv6].src
            self.dst = packet[IPv6].dst
        else:
            return False
        return True

    def parse_transport(self, packet):
        if packet.haslayer(TCP):
            self.sport = packet[TCP].sport
            self.dport = packet[TCP].dport
        elif packet.haslayer(UDP):
            self.sport = packet[UDP].sport
            self.dport = packet[UDP].dport
        else:
            return False
        return True

    def parse_application(self, packet, protocol_decoder: ProtocolDecoder):

        if packet.haslayer(scapy.Raw):
            raw_layer = packet[scapy.Raw].load
            decoded_layer = protocol_decoder.decode_packet(self.sport, self.dport, raw_layer)
            if decoded_layer:
                self.proto = decoded_layer[0]
                self.header = decoded_layer[1]
                self.subject = decoded_layer[2]
                self.content = decoded_layer[3]
                return True
        return False

    def set_mark(self, mark):
        self.mark = mark