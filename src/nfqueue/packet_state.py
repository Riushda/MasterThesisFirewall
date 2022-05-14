from enum import Enum

from nfqueue.abstract_packet import AbstractPacket


# this class check that all packets are protocol compliant and save the state of requests/subscriptions made
class PacketState:
    def __init__(self, protocol_decoder):
        self.requests = {}
        self.subscriptions = {}
        self.protocol_decoder = protocol_decoder

    def handle_packet(self, packet: AbstractPacket):

        if self.protocol_decoder.ask_protocol(packet, "is_pull_packet"):

            if self.protocol_decoder.ask_protocol(packet, "is_request"):
                self.protocol_decoder.ask_protocol(packet, "add_request", self)
                # print("Packet state log: Request added")
                # do not update context, with pull protocol response is always needed to check if request was successful
                return Verdict.ALLOW_WITH_CONSTRAINT.value

            elif self.protocol_decoder.ask_protocol(packet, "is_response"):

                request_packet = self.protocol_decoder.ask_protocol(packet, "match_request", self)
                if request_packet:
                    # print("Packet state log: Response matched")

                    # allow and update context if request was successful
                    return True, True, self.protocol_decoder.ask_protocol(packet, "is_request_successful",
                                                                          request_packet)
                else:
                    # print("Packet state log: Response not matched")
                    return Verdict.DROP.value  # if response doesn't match any previous request, drop it

            else:
                # neither a request nor a response

                # action can be triggered by the protocol when it sees a certain signaling packet
                # print("Packet state log: Pull packet signaling")
                return self.protocol_decoder.ask_protocol(packet, "update_packet_state", self), False, False

        elif self.protocol_decoder.ask_protocol(packet, "is_push_packet"):

            if self.protocol_decoder.ask_protocol(packet, "is_subscribe_packet"):
                self.protocol_decoder.ask_protocol(packet, "add_subscription", self)
                # print("Packet state log: Subscription added")
                return Verdict.ALLOW.value

            elif self.protocol_decoder.ask_protocol(packet, "is_publish_packet"):

                subscription_packet = self.protocol_decoder.ask_protocol(packet, "match_subscription", self)
                if subscription_packet:
                    # print("Packet state log: Publish matched")
                    # update context only if publish don't come from a broker (avoid updating the context many times with same publish)
                    return True, True, not self.protocol_decoder.ask_protocol(packet, "from_broker")
                else:
                    if self.protocol_decoder.ask_protocol(packet, "toward_broker"):
                        # if publish toward a broker, accept it
                        # update the context only with publish message from publisher to broker
                        # print("Packet state log: Publish toward broker")
                        return Verdict.ALLOW_AND_UPDATE_CONTEXT.value
                    else:
                        # print("Packet state log: Publish not matched")
                        return Verdict.DROP.value  # if publish toward client which doesn't match any subscription, drop it

            else:
                # neither subscribe message nor publish message

                # action can be triggered by the protocol when it sees a certain signaling packet
                # print("Packet state log: Push packet signaling")
                return self.protocol_decoder.ask_protocol(packet, "update_packet_state", self), False, False
        else:
            pass  # should never reach there

        # print("Packet state log: Neither push packet nor pull packet")
        return Verdict.ALLOW.value  # cannot find what it is (request, response, subscription or publish) then allow it and don't update context with it

    def add_request(self, packet: AbstractPacket, key):
        self.requests[(packet.src, packet.dst, packet.proto, key)] = packet

    def remove_request(self, packet: AbstractPacket, key):
        # src and dst inverted because we remove when the response arrives
        self.requests.pop((packet.src, packet.dst, packet.proto, key))

    def add_subscription(self, packet: AbstractPacket, key):
        # print("Packet state log: Added subscription - " + str((packet.src, packet.dst, packet.proto, key)))
        self.subscriptions[(packet.src, packet.dst, packet.proto, key)] = {"valid": False, "can_remove": False,
                                                                           "packet": packet}

    def remove_subscription(self, packet: AbstractPacket, key):
        # print("Packet state log: subscription removed")
        self.subscriptions.pop((packet.src, packet.dst, packet.proto, key))

    def remove_client_subscriptions(self, packet: AbstractPacket):
        for key in list(self.subscriptions.keys()):
            if key[1] == packet.src:
                del self.subscriptions[key]

    # pull packet matching

    def has_request(self, packet, key):

        # src and dst inverted because check done with response
        packet_request: AbstractPacket = self.requests.get((packet.dst, packet.src, packet.proto, key))
        if packet_request:
            return packet_request
        return None

    # push packet matching

    def has_subscription(self, packet, key):

        # src and dst inverted because check done with publish
        # print("Packet state log: has_subscription: " + str((packet.dst, packet.src, packet.proto, key)))
        packet_subscription: AbstractPacket = self.subscriptions.get((packet.dst, packet.src, packet.proto, key))
        if packet_subscription:
            return packet_subscription
        return None


class Verdict(Enum):
    DROP = False, False, False
    ALLOW = True, False, False
    ALLOW_WITH_CONSTRAINT = True, True, False
    ALLOW_AND_UPDATE_CONTEXT = True, True, True
