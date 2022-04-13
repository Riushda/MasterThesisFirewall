from multiprocessing import Queue

from netfilterqueue import NetfilterQueue, Packet
from scapy.layers.inet import IP

from nfqueue.abstract_packet import AbstractPacket
from nfqueue.packet_state import PacketState
from nfqueue.protocol_decoder import ProtocolDecoder
from utils.constant import *


class PacketHandler:
    def __init__(self, queue: Queue, mapping):
        self.packet_queue = queue
        self.default_policy = Policy.ACCEPT.value
        self.mapping = mapping
        self.protocol_decoder = ProtocolDecoder() # protocol decoder supporting many different protocols
        self.protocol_decoder.add_broker("192.168.33.11", "mqtt")
        self.request_state = PacketState(self.protocol_decoder)  # stateful object for maintaining request/response state

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
            print(abstract_packet)
            allowed_packet, context = self.request_state.handle_packet(abstract_packet)

            if allowed_packet: # if packet is legitimate (request or response linked to a previously made request)

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

                if context: # if packet response of a previously made request or just a push message (with complete information)
                    self.packet_queue.put(abstract_packet)

                return

            else:
                raw_packet.drop()
                return

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
