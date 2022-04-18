from multiprocessing import Queue

from netfilterqueue import NetfilterQueue, Packet
from scapy.layers.inet import IP

from nfqueue.abstract_packet import AbstractPacket
from nfqueue.constraint_mapping import ConstraintMapping
from nfqueue.packet_state import PacketState
from nfqueue.protocol_decoder import ProtocolDecoder
from utils.constant import *


class PacketHandler:
    def __init__(self, queue: Queue, constraint_mapping):
        self.packet_queue = queue
        self.mapping = constraint_mapping
        self.protocol_decoder = ProtocolDecoder()  # protocol decoder supporting many different protocols
        self.protocol_decoder.add_broker("192.168.33.11", "mqtt")
        self.packet_state = PacketState(self.protocol_decoder)  # stateful object for maintaining request/response state

    def handle_packet(self, raw_packet: Packet):
        abstract_packet = AbstractPacket()
        decoded_packet = IP(raw_packet.get_payload())

        if not abstract_packet.parse_network(decoded_packet):
            # should never reach there because only IP packets are hooked
            raw_packet.accept()
            return

        #print(f"src: {str(abstract_packet.src)} ~ dst: {str(abstract_packet.dst)}")

        if not abstract_packet.parse_transport(decoded_packet):
            print("Unknown transport layer protocol")

        if abstract_packet.parse_application(decoded_packet, self.protocol_decoder):
            print(abstract_packet)

            allowed_packet, context = self.packet_state.handle_packet(abstract_packet)

            if allowed_packet:  # if packet is legitimate (request or response linked to a previously made request)

                if context:  # if packet response of a previously made request or just a push message (with complete information)

                    abstract_packet.set_mark(raw_packet.get_mark())
                    decision = self.mapping.decision(abstract_packet)

                    # The packet has an app layer which matches
                    if decision == Policy.ACCEPT:
                        print("Packet accepted!")
                        raw_packet.accept()
                    # The packet has an app layer which does not match
                    else:
                        print("Packet dropped!")
                        raw_packet.drop()
                        return

                    self.packet_queue.put(abstract_packet)

                else:
                    # accept packet which doesn't trigger context without constraint matching
                    print("Packet accepted!")
                    raw_packet.accept()

                return
            else:
                raw_packet.drop()
                return

        # This can be reached if this is a signal packet such as SYN/ACK
        raw_packet.accept()


class HandlingQueue:
    def __init__(self):
        self.packet_queue = Queue()
        self.nf_queue = NetfilterQueue()
        self.constraint_mapping = ConstraintMapping()
        self.packet_handler = PacketHandler(self.packet_queue, self.constraint_mapping)
        self.keep_running = True

    def run(self):
        self.nf_queue.bind(0, self.packet_handler.handle_packet)
        while self.keep_running:
            self.nf_queue.run(block=False)
        self.nf_queue.unbind()

    def stop(self):
        self.keep_running = False
