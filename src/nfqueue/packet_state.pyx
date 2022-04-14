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
                print("request added")
                # do not update context, with pull protocol response is always needed to check if request was successful
                return True, False

            elif self.protocol_decoder.ask_protocol(packet, "is_response"):

                request_packet = self.protocol_decoder.ask_protocol(packet, "match_request", self)
                if request_packet:
                    print("response matched")

                    # allow and update context if request was successful
                    return True, not self.protocol_decoder.ask_protocol(packet, "is_request_successful", request_packet)
                else:
                    print("response not matched")
                    return False, False # if response doesn't match any previous request, drop it

            else:
                # neither a request nor a response

                # action can be triggered by the protocol when it sees a certain signaling packet
                self.protocol_decoder.ask_protocol(packet, "update_packet_state", self)
                print("pull packet signaling")
                return True, False

        elif self.protocol_decoder.ask_protocol(packet, "is_push_packet"):

            if self.protocol_decoder.ask_protocol(packet, "is_subscribe_packet"):
                self.protocol_decoder.ask_protocol(packet, "add_subscription", self)
                print("subscription added")
                return True, False

            elif self.protocol_decoder.ask_protocol(packet, "is_publish_packet"):

                subscription_packet = self.protocol_decoder.ask_protocol(packet, "match_subscription", self)
                if subscription_packet:
                    print("publish matched")
                    return True, True # update the context only with publish message for push protocols
                else:
                    if self.protocol_decoder.ask_protocol(packet, "toward_broker"):
                        # if publish toward a broker, accept it
                        print("publish toward broker")
                        return True, False
                    else:
                        print("publish not matched")
                        return False, False # if publish toward client which doesn't match any subscription, drop it

            else:
                # neither subscribe message nor publish message

                # action can be triggered by the protocol when it sees a certain signaling packet
                self.protocol_decoder.ask_protocol(packet, "update_packet_state", self)
                print("push packet signaling")
                return True, False
        else:
            pass # should never reach there

        print("neither push packet nor pull packet")
        return True, False # cannot find what it is (request, response, subscription or publish) then allow it and don't update context with it

    def add_request(self, packet: AbstractPacket, key):
        self.requests[(packet.src, packet.dst, packet.proto, key)] = packet

    def remove_request(self, packet: AbstractPacket, key):
        # src and dst inverted because we remove when the response arrives
        self.requests.pop((packet.src, packet.dst, packet.proto, key))

    def add_subscription(self, packet: AbstractPacket, key):
        print("subscription added : "+str((packet.src, packet.dst, packet.proto, key)))
        self.subscriptions[(packet.src, packet.dst, packet.proto, key)] = packet

    def remove_subscription(self, packet: AbstractPacket, key):
        print("subscription removed")
        self.subscriptions.pop((packet.src, packet.dst, packet.proto, key))

    def remove_client_subscriptions(self, packet: AbstractPacket):
        for key in list(self.subscriptions.keys()):
            if key[1]==packet.src:
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
        packet_subscription: AbstractPacket = self.subscriptions.get((packet.dst, packet.src, packet.proto, key))
        if packet_subscription:
            return packet_subscription
        return None