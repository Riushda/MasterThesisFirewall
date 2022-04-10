from multiprocessing import Queue

from netfilterqueue import NetfilterQueue, Packet
from scapy.layers.inet import IP

from nfqueue.abstract_packet import AbstractPacket
from nfqueue.request_state import RequestState
from nfqueue.protocol_decoder import ProtocolDecoder
from utils.constant import *


class PacketHandler:
    def __init__(self, queue: Queue, mapping):
        self.packet_queue = queue
        self.default_policy = Policy.ACCEPT.value
        self.mapping = mapping
        self.pull_protocol_handler = RequestState() # stateful object for pull protocols
        self.protocol_decoder = ProtocolDecoder() # protocol decoder supporting many different protocols

    def set_default(self, policy):
        self.default_policy = policy

    def apply_default(self, packet: Packet):
        if self.default_policy == Policy.ACCEPT.value:
            packet.accept()
        if self.default_policy == Policy.DROP.value:
            packet.drop()

    def handle_packet(self, raw_packet: Packet):
        abstract_packet = AbstractPacket()
        decoded_packet = IP(raw_packet.get_payload())

        if not abstract_packet.parse_network(decoded_packet):
            # should never reach there because ethernet packets are not hooked
            raw_packet.accept()
            return

        #print(f"src: {str(abstract_packet.src)} ~ dst: {str(abstract_packet.dst)}")

        if not abstract_packet.parse_transport(decoded_packet):
            print("Unknown transport layer protocol")

        if abstract_packet.parse_application(decoded_packet, self.protocol_decoder):

            #forbidden_pull_packet = self.pull_protocol_handler.handle_packet(abstract_packet)

            #if not forbidden_pull_packet: # if packet from a push protocol or a rightful pull packet

            abstract_packet.set_mark(str(raw_packet.get_mark()))
            decision = self.mapping.decision(abstract_packet)

            if decision == Policy.ACCEPT.value:
                print("Accept!")
                raw_packet.accept()
            elif decision == Policy.DROP.value:
                print("Drop!")
                raw_packet.drop()
                return
            elif decision == Policy.DEFAULT.value:
                print("Default!")
                self.apply_default(raw_packet)
                return

            self.packet_queue.put(abstract_packet)
            return

            #else:
            #    raw_packet.drop()

        self.apply_default(raw_packet)


def run(queue: Queue, mapping):
    packet_queue = queue
    packet_handler = PacketHandler(packet_queue, mapping)

    nfqueue = NetfilterQueue()
    nfqueue.bind(0, packet_handler.handle_packet)
    try:
        nfqueue.run()
    except KeyboardInterrupt:
        nfqueue.unbind()
