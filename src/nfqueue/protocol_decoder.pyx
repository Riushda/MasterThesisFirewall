import re
from enum import Enum

from nfqueue.mqtt_decoder import MQTTDecoder
from nfqueue.coap_decoder import CoAPDecoder

class ProtocolDecoder:
	def __init__(self):
		self.pattern = re.compile('\??([\w.-]+)[=]?([\w.-]+)?&?', re.IGNORECASE) # \??(\w+)=(\w+)&? # \??(\w+)[=]?(\w+)?&?
		self.mqtt_decoder = MQTTDecoder()
		self.coap_decoder = CoAPDecoder()

	def decode_packet(self, sport, dport, app_layer):
		decoded = None
		if dport==self.mqtt_decoder.port : # if MQTT
			decoded = self.mqtt_decoder.decode(app_layer)

		elif sport==self.coap_decoder.port or dport==self.coap_decoder.port: # if CoAP
			decoded = self.coap_decoder.decode(app_layer)

		if decoded is not None and decoded[-1] is not None:
			decoded[-1] = self.decode_payload(decoded[-1])

		print(decoded)

		return decoded

	def decode_payload(self, payload):
		groups = self.pattern.findall(payload)

		for i in range(len(groups)):
			if len(groups[i]) > 1 and groups[i][1] == "":
				groups[i] = groups[i][:-1]  # pop second element if only value

		return groups

	def is_pull_packet(self, packet):
		if packet.proto==Protocols.MQTT:
			return self.mqtt_decoder.is_pull_packet(packet)
		elif packet.proto==Protocols.CoAP:
			pass

class Protocols(Enum):
	MQTT = "mqtt"
	CoAP = "coap"
