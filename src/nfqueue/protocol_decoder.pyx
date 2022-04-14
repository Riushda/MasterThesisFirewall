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

		if decoded is not None and len(decoded) > 0 and len(decoded[-1]) > 0:
			decoded[-1] = self.decode_payload(decoded[-1])

		print(decoded)

		return decoded

	def decode_payload(self, payload):
		groups = self.pattern.findall(payload)

		for i in range(len(groups)):
			if len(groups[i]) > 1 and groups[i][1] == "":
				groups[i] = groups[i][:-1]  # pop second element if only value

		return groups

	def ask_protocol(self, packet, function, *args):
		for decoder in self.decoder_list:
			if packet.proto==decoder.protocol_name:
				if hasattr(decoder, function):
					if len(args) == 0:
						return getattr(decoder, function)(packet)
					else:
						return getattr(decoder, function)(packet, args)
				else:
					break

		return False

	def add_broker(self, ip, proto):
		for decoder in self.decoder_list:
			if proto==decoder.protocol_name:
				if hasattr(decoder, "broker_list"):
					decoder.broker_list.append(ip)
				break