from multiprocessing import Queue

from netfilterqueue import NetfilterQueue, Packet
from scapy.layers.inet import IP

from nfqueue.abstract_packet import AbstractPacket
from nfqueue.packet_state import PacketState
from nfqueue.protocol_decoder import ProtocolDecoder
from nfqueue.relation_mapping import RelationMapping
from client.constant import *


class PacketHandler:
    def __init__(self, queue: Queue, relation_mapping, members):
        self.packet_queue = queue
        self.mapping = relation_mapping
        self.protocol_decoder = ProtocolDecoder()  # protocol decoder supporting many different protocols
        for _, member in members.items():
            if member.port == 1883:
                self.protocol_decoder.add_broker(member.ip, "mqtt")
        self.packet_state = PacketState(self.protocol_decoder)  # stateful object for maintaining request/response state

    def handle_packet(self, raw_packet: Packet):
        abstract_packet = AbstractPacket()
        decoded_packet = IP(raw_packet.get_payload())
        if not abstract_packet.parse_network(decoded_packet):
            # should never reach there because only IP packets are hooked
            raw_packet.accept()
            return

        if not abstract_packet.parse_transport(decoded_packet):
            print("Handling queue log: Unknown transport layer protocol")

        if abstract_packet.parse_application(decoded_packet, self.protocol_decoder):

            allowed_packet, constraint, context = self.packet_state.handle_packet(abstract_packet)

            if allowed_packet:  # if packet is legitimate (request or response linked to a previously made request)

                if constraint:  # if packet response of a previously made request or just a push message (with complete information)

                    abstract_packet.set_mark(raw_packet.get_mark())
                    decision = self.mapping.decision(abstract_packet)

                    # The packet has an app layer which matches
                    if decision == Policy.ACCEPT:
                        # print("Handling queue log: Packet accepted!")
                        raw_packet.accept()
                    # The packet has an app layer which does not match
                    else:
                        # print("Handling queue log: Packet dropped!")
                        raw_packet.drop()
                        return

                    if context:
                        self.packet_queue.put(abstract_packet)

                else:
                    # accept packet which doesn't trigger context without constraint matching
                    # print("Handling queue log: Packet accepted!")
                    raw_packet.accept()

                return
            else:
                # print("Handling queue log: Packet dropped!")
                raw_packet.drop()
                return

        # This can be reached if this is a signal packet such as SYN/ACK
        raw_packet.accept()


class HandlingQueue:
    def __init__(self, relation_mapping: RelationMapping, members):
        self.packet_queue = Queue()
        self.nf_queue = NetfilterQueue()
        self.packet_handler = PacketHandler(self.packet_queue, relation_mapping, members)
        self.keep_running = True

    def run(self):
        self.nf_queue.bind(0, self.packet_handler.handle_packet)
        while self.keep_running:
            self.nf_queue.run(block=False)
        self.nf_queue.unbind()

    def stop(self):
        self.keep_running = False

# "broker": "broker",
