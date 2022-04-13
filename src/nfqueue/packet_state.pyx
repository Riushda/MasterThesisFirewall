from nfqueue.abstract_packet import AbstractPacket
from nfqueue.protocol_decoder import ProtocolDecoder

# this class check that all packets are protocol compliant and save the state of requests/subscriptions made
class PacketState:
    def __init__(self, protocol_decoder):
        self.requests = {}
        self.subscriptions = {}
        self.protocol_decoder = protocol_decoder

    def handle_packet(self, packet: AbstractPacket):

        if self.protocol_decoder.ask_protocol(packet, "is_pull_packet"):

            if self.protocol_decoder.ask_protocol(packet, "is_request"):
                self.add_request(packet)
                # do not update context, with pull protocol response is always needed to check if request was successful
                return True, False

            elif self.protocol_decoder.ask_protocol(packet, "is_response"):

                request_packet = self.has_request(packet)
                if packet is not None and self.protocol_decoder.ask_protocol(packet, "match_request", request_packet):
                    self.remove_request(packet)

                    # allow and update context if request was successful
                    return True, not self.protocol_decoder.ask_protocol(packet, "is_request_successful", request_packet)
                else:
                    return False, False # if response doesn't match any previous request, drop it

            else:
                # neither a request nor a response

                # action can be triggered by the protocol when it sees a certain signaling packet
                self.protocol_decoder.ask_protocol(packet, "update_packet_state", self)
                return True, False

        elif self.protocol_decoder.ask_protocol(packet, "is_push_packet"):

            if self.protocol_decoder.ask_protocol(packet, "is_subscribe_packet"):
                self.add_subscription(packet) # TODO for mqtt should way for suback
                return True, False

            elif self.protocol_decoder.ask_protocol(packet, "is_publish_packet"):

                subscription_packet = self.has_subscription(packet)
                if subscription_packet is not None:

                    if self.protocol_decoder.ask_protocol(packet, "match_subscription", subscription_packet):
                        print("publish accepted")
                        return True, True # update the context only with publish message for push protocols
                    else:
                        print("publish dropped")
                        return False, False # unauthorized publish message (there are no related subscribe message)
                else:
                    if self.protocol_decoder.ask_protocol(packet, "toward_broker"):
                        # if publish toward a broker, accept it
                        return True, False
                    else:
                        print("publish no subscription")
                        return False, False # if publish toward client which doesn't match any subscription, drop it

            else:
                # neither subscribe message nor publish message

                # action can be triggered by the protocol when it sees a certain signaling packet
                self.protocol_decoder.ask_protocol(packet, "update_packet_state", self)
                return True, False
        else:
            pass # should never reach there

        return True, False # cannot find what it is (request, response, subscription or publish) then allow it and don't update context with it

    def add_request(self, packet: AbstractPacket):
        msg_id = self.protocol_decoder.ask_protocol(packet, "get_msg_id")
        self.requests[(packet.src, packet.dst, packet.proto, msg_id)] = packet

    def remove_request(self, packet: AbstractPacket):
        msg_id = self.protocol_decoder.ask_protocol(packet, "get_msg_id")

        # src and dst inverted because we remove when the response arrives
        self.requests.pop((packet.dst, packet.src, packet.proto, msg_id))

    def add_subscription(self, packet: AbstractPacket):
        print("subscription added : "+str((packet.src, packet.dst, packet.proto, packet.subject)))
        self.subscriptions[(packet.src, packet.dst, packet.proto, packet.subject)] = packet

    def remove_subscription(self, packet: AbstractPacket):
        print("subscription removed")
        self.subscriptions.pop((packet.src, packet.dst, packet.proto, packet.subject))

    def remove_client_subscriptions(self, packet: AbstractPacket):
        for key in list(self.subscriptions.keys()):
            if key[1]==packet.src:
                del self.subscriptions[key]

    # pull packet matching

    def has_request(self, packet):
        msg_id = self.protocol_decoder.ask_protocol(packet, "get_msg_id")

        # src and dst inverted because check done with response
        packet_request: AbstractPacket = self.requests.get((packet.dst, packet.src, packet.proto, msg_id))
        if packet_request:
            return packet_request
        return None

    # push packet matching

    def has_subscription(self, packet):
        # src and dst inverted because check done with publish
        print("has subscription : " + str((packet.dst, packet.src, packet.proto, packet.subject)))
        packet_subscription: AbstractPacket = self.subscriptions.get((packet.dst, packet.src, packet.proto, packet.subject))
        if packet_subscription:
            return packet_subscription
        return None