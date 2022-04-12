from nfqueue.abstract_packet import AbstractPacket
from nfqueue.protocol_decoder import ProtocolDecoder

# this class check that all packets are protocol compliant and save the state of requests/subscriptions made
class PacketState:
    def __init__(self, protocol_decoder):
        self.requests = {}
        self.subscriptions = {}
        self.protocol_decoder = protocol_decoder

    def handle_packet(self, packet: AbstractPacket):

        if self.protocol_decoder.ask_protocol(self, packet, "is_pull_packet"):

            if self.protocol_decoder.ask_protocol(self, packet, "is_request"):
                self.add_request(packet)
                # ask if the information in the packet is complete, that we shouldn't wait for the content of the response to update the context
                # for instance, post message in coap already contains all the information but not the get message
                return True, self.protocol_decoder.ask_protocol(self, packet, "is_complete")

            elif self.protocol_decoder.ask_protocol(self, packet, "is_response"):

                request_packet = self.has_request(packet)
                if packet is not None and self.protocol_decoder.ask_protocol(self, packet, "match_request", request_packet = request_packet):
                    packet.subject = request_packet.subject # in some pull protocols (like coap) the subject is not present in the response
                    self.remove_request(packet)

                    # allow and update context if request wasn't complete
                    return True, not self.protocol_decoder.ask_protocol(self, request_packet, "is_complete")
                else:
                    return False, False # if response doesn't match any previous request, drop it

            else:
                # neither a request nor a response
                self.protocol_trigger(packet) # action can be triggered by the protocol when it sees a certain signaling packet
                return True, False

        elif self.protocol_decoder.ask_protocol(self, packet, "is_push_packet"):

            if self.protocol_decoder.ask_protocol(self, packet, "is_subscribe_packet"):
                self.add_subscription(packet)
                return True, False

            elif self.protocol_decoder.ask_protocol(self, packet, "is_publish_packet"):

                subscription_packet = self.has_subscription(packet)
                if subscription_packet is not None:

                    if self.protocol_decoder.ask_protocol(self, packet, "match_subscription", subscription_packet = subscription_packet):
                        return True, True # update the context only with publish message for push protocols
                    else:
                        return False, False # unauthorized publish message (there are no related subscribe message)
                else:
                    return False, False # if publish doesn't match any subscription, drop it

            else:
                # neither subscribe message nor publish message
                self.protocol_trigger(packet) # action can be triggered by the protocol when it sees a certain signaling packet
                return True, False
        else:
            pass # should never reach there

        return True, False # cannot find what it is (request, response, subscription or publish) then allow it and don't update context with it

    def add_request(self, packet: AbstractPacket):
        msg_id = self.protocol_decoder.ask_protocol(self, packet, "get_msg_id")
        self.requests[(packet.src, packet.dst, packet.proto, msg_id)] = packet

    def remove_request(self, packet):
        msg_id = self.protocol_decoder.ask_protocol(self, packet, "get_msg_id")

        # src and dst inverted because we remove when the response arrives
        self.requests.pop((packet.dst, packet.src, packet.proto, msg_id))

    def add_subscription(self, packet: AbstractPacket):
        self.subscriptions[(packet.src, packet.dst, packet.proto, packet.subject)] = packet

    def remove_subscription(self, packet: AbstractPacket):
        self.subscriptions.pop((packet.src, packet.dst, packet.proto, packet.subject))

    def remove_client_subscriptions(self, packet: AbstractPacket):
        for key in list(self.subscriptions.keys()):
            if key[1]==packet.src:
                del self.subscriptions[key]

    def protocol_trigger(self, packet):
        function = self.protocol_decoder.ask_protocol(self, packet, "ask_trigger")
        if hasattr(self, function):
            getattr(self, function)(packet)

    # pull packet matching

    def has_request(self, packet, protocol_decoder: ProtocolDecoder):
        msg_id = protocol_decoder.ask_protocol(self, packet, "get_msg_id")

        # src and dst inverted because check done with response
        packet_request: AbstractPacket = self.requests.get((packet.dst, packet.src, packet.proto, msg_id))
        if packet_request:
            return packet_request
        return None

    # push packet matching

    def has_subscription(self, packet):
        # src and dst inverted because check done with publish
        packet_subscription: AbstractPacket = self.subscriptions.get((packet.dst, packet.src, packet.proto, packet.subject))
        if packet_subscription:
            return packet_subscription
        return None