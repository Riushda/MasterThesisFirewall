from enum import Enum

class MQTTDecoder:

	# MQTT layer
	# for more information see https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html#_Toc3901019
	# Remark : msg_len is the length of the remaining fields (not counting itself)
	#  _______________________________________________________________________________________
	# |        |         |           |                   |                                    |
	# | header | msg_len | topic_len |      topic        |              payload               |
	# | 1 byte | 1 byte  |  2 bytes  | topic_len byte(s) |  (msg_len - 2 - topic_len) byte(s) |
	# |________|_________|___________|___________________|____________________________________|
	#
	# control_header format (4 last bits only used by publish messages) :
	#             ____________________________________
	#   bits :   |      7-4	    |  3  | 2  1 |   0    |
	# 		     | Message Type | DUP | QoS  | RETAIN |
	#			 |____________________________________|
	#

	def __init__(self):
		self.protocol_name = "mqtt"
		self.port = 1883

	def match_protocol(self, sport, dport):
		return dport==self.port

	def decode(self, app_layer):
		header = {}

		control_header = app_layer[0]

		header["control_header_type"] = control_header >> 4
		header["control_header_flag"] = control_header & 15

		if MQTTMessageType(header["control_header_type"]) == MQTTMessageType.PUBLISH :

			header["DUP"] = header["control_header_flag"] & 8
			header["QOS"] = header["control_header_flag"] & 6
			header["RETAIN"] = header["control_header_flag"] & 1

			msg_len : int = app_layer[1]
			topic_len : int = int.from_bytes(app_layer[2:4], byteorder='big')

			offset = 4

			topic = app_layer[offset:offset+topic_len].decode("utf-8")
			offset += topic_len

			payload_len = msg_len - 2 - topic_len
			payload = app_layer[offset:offset+payload_len].decode("utf-8")
			if payload is None:
				payload = []

			return ["mqtt", header, topic, payload]

		return None

	# functions for pull packets

	def is_pull_packet(self, packet):
		return False # mqtt is push only

	# function for push packets

	def is_push_packet(self, packet):
		return True # mqtt is push only

	def is_subscribe_packet(self, packet):
		return MQTTMessageType(packet.header["control_header_type"]) == MQTTMessageType.SUBSCRIBE

	def is_publish_packet(self, packet):
		return MQTTMessageType(packet.header["control_header_type"]) == MQTTMessageType.PUBLISH

	def is_unsubscribe_packet(self, packet):
		return MQTTMessageType(packet.header["control_header_type"]) == MQTTMessageType.UNSUBSCRIBE

	def is_connect_packet(self, packet):
		return MQTTMessageType(packet.header["control_header_type"]) == MQTTMessageType.CONNECT

	def is_disconnect_packet(self, packet):
		return MQTTMessageType(packet.header["control_header_type"]) == MQTTMessageType.DISCONNECT

	# make further verification, specific to the protocol
	def match_subscription(self, packet, subscription_packet):
		return True # if ip and subject matches, then no further verification possible

	# this can trigger function in the packet_state class depending on the type of the packet
	def ask_trigger(self, packet):
		if self.is_unsubscribe_packet(packet):
			return "remove_subscription"
		elif self.is_disconnect_packet(packet):
			# if disconnected, client unsubscribe from all topics, this behavior can be changed
			return "remove_client_subscriptions"
		elif self.is_connect_packet(packet):
			pass # Nothing to do for the moment

		return "None" # do not trigger anything

class MQTTMessageType(Enum):
	RESERVED = 0
	CONNECT = 1
	CONNACK = 2
	PUBLISH = 3
	PUBACK = 4
	PUBREC = 5
	PUBREL = 6
	PUBCOMP = 7
	SUBSCRIBE = 8
	SUBACK = 9
	UNSUBSCRIBE = 10
	UNSUBACK = 11
	PINGREQ = 12
	PINGRESP = 13
	DISCONNECT = 14
	AUTH = 15