from nfqueue.abstract_packet import AbstractPacket
from nfqueue.protocol_decoder import ProtocolDecoder


class PacketState:
    def __init__(self):
        self.requests = {}
        self.subscriptions = {}

    def handle_packet(self, packet: AbstractPacket, protocol_decoder: ProtocolDecoder):

        if protocol_decoder.ask_protocol(self, packet, "is_pull_packet"):

            if protocol_decoder.ask_protocol(self, packet, "is_request"):
                self.add_request(packet)

            elif protocol_decoder.ask_protocol(self, packet, "is_response"):

                request_packet = self.has_request(packet)
                if packet is not None and protocol_decoder.ask_protocol(self, packet, "match_request", request_packet = request_packet):
                    self.remove_request(packet)
                else:
                    return False # if response doesn't match any previous request, drop it
            else:
                pass # neither a request nor a response

        elif protocol_decoder.ask_protocol(self, packet, "is_push_packet"):
            subscription_packet = self.has_subscription(packet)
            if subscription_packet is not None:
                return protocol_decoder.ask_protocol(self, packet, "match_subscription", subscription_packet = subscription_packet)
            else:
                return False # if publish doesn't match any subscription, drop it
        else:
            pass # should never reach there

        return True

    def add_request(self, packet: AbstractPacket, msg_id):
        self.requests[(packet.src, packet.dst, packet.proto, msg_id)] = packet

    def remove_request(self, packet, msg_id):
        self.requests.pop((packet.dst, packet.src, packet.proto, msg_id))

    # pull packet matching

    def has_request(self, packet, protocol_decoder: ProtocolDecoder):
        msg_id = protocol_decoder.ask_protocol(self, packet, "get_msg_id")
        packet_request: AbstractPacket = self.requests.get((packet.dst, packet.src, packet.proto, msg_id))
        if packet_request:
            return packet_request
        return None

    # push packet matching

    def has_subscription(self, packet):
        packet_subscription: AbstractPacket = self.subscriptions.get((packet.dst, packet.src, packet.proto, packet.subject))
        if packet_subscription:
            return packet_subscription
        return None