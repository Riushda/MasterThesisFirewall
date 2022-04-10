from nfqueue.abstract_packet import AbstractPacket

class RequestState:
    def __init__(self):
        self.requests = {}

    def handle_packet(self, packet: AbstractPacket):

        if self.is_pull_packet(packet):

            msg_id = self.get_msg_id()

            if self.is_request(packet.header):
                self.add_request(packet)

            elif self.is_response(packet.header):

                packet.subject = self.match_response(packet, msg_id)
                if packet.subject is not None:
                    self.remove_request(packet)
                else:
                    return False # if response doesn't match any previous request, drop it
            else:
                pass # neither a request nor a response

        return True

    def is_pull_packet(self, packet):
        return

    def is_request(self, app_layer):
        return -1

    def is_response(self, app_layer):
        return -1

    def get_msg_id(self, app_layer):
        return 0

    def add_request(self, packet: AbstractPacket, msg_id):
        self.requests[(packet.src, packet.dst, packet.proto, msg_id)] = packet

    def remove_request(self, packet, msg_id):
        self.requests.pop((packet.dst, packet.src, packet.proto, msg_id))

    def match_response(self, packet, msg_id):
        packet_request: AbstractPacket = self.requests.get((packet.dst, packet.src, packet.proto, msg_id))
        if packet_request:
            return packet_request.subject
        return None