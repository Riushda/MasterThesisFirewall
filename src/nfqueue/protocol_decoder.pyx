import re

from nfqueue.mqtt_decoder import MQTTDecoder
from nfqueue.coap_decoder import CoAPDecoder

class ProtocolDecoder:
	def __init__(self):
		self.pattern = re.compile('\??([\w.-]+)[=]?([\w.-]+)?&?', re.IGNORECASE) # \??(\w+)=(\w+)&? # \??(\w+)[=]?(\w+)?&?
		self.decoder_list = [MQTTDecoder(), CoAPDecoder()]

	def decode_packet(self, sport, dport, app_layer):

		decoded = None
		for decoder in self.decoder_list:
			if decoder.match_protocol(sport, dport):
				decoded = decoder.decode(app_layer)
				break

		if decoded is not None and len(decoded[-1])>0:
			decoded[-1] = self.decode_payload(decoded[-1])

		print(decoded)
		return decoded

	def decode_payload(self, payload):
		groups = self.pattern.findall(payload)

		for i in range(len(groups)):
			if len(groups[i]) > 1 and groups[i][1] == "":
				groups[i] = groups[i][:-1]  # pop second element if only value

		return groups

	def ask_protocol(self, packet, function, **kwargs):
		for decoder in self.decoder_list:
			if packet.proto==decoder.protocol_name:

				# functions for pull packets
				if function=="is_pull_packet":
					return decoder.is_pull_packet(packet)
				elif function=="is_request":
					return decoder.is_request(packet)
				elif function=="is_response":
					return decoder.is_response(packet)
				elif function=="get_msg_id":
					return decoder.get_msg_id(packet)
				elif function=="match_request":
					return decoder.match_request(packet, kwargs["request_packet"])

				# function for push packets
				elif function=="is_push_packet":
					return decoder.is_push_packet(packet)
				elif function=="match_subscription":
					return decoder.match_subscription(packet, kwargs["subscription_packet"])
				else:
					pass

		return False
