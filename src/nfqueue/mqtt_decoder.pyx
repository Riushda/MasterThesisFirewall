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

		# fixed header

		if len(app_layer) < 2:
			return None # app_layer too small

		control_header = app_layer[0]

		msg_len: int = app_layer[1]

		offset = 2

		if len(app_layer) < offset + msg_len:
			return None  # app_layer too small

		header["control_header_type"] = control_header >> 4
		header["control_header_flag"] = control_header & 15

		if not MQTTMessageType.has_type(header["control_header_type"]):
			return None # unknown message type

		if MQTTMessageType(header["control_header_type"]) == MQTTMessageType.PUBLISH:
			header["DUP"] = header["control_header_flag"] & 8
			header["QOS"] = header["control_header_flag"] & 6
			header["RETAIN"] = header["control_header_flag"] & 1

		# variable header
		## packet_identifier

		if MQTTMessageType.has_packet_identifier(MQTTMessageType(header["control_header_type"]), header.get("QOS", None)):
			if len(app_layer) < offset + 2:
				return None  # app_layer too small

			header["packet_identifier"] = int.from_bytes(app_layer[offset:offset + 2], byteorder='big')
			offset += 2

		## connect fields

		if MQTTMessageType(header["control_header_type"]) == MQTTMessageType.CONNECT:
			decoded_length = self.decode_connect_variable_header(header, app_layer, offset)
			if decoded_length:
				offset += decoded_length
			else:
				return None

		topic_len = 0
		topic = None
		if MQTTMessageType.has_topic(MQTTMessageType(header["control_header_type"])):
			if len(app_layer) < offset + 2:
				return None  # app_layer too small
			topic_len : int = int.from_bytes(app_layer[offset:offset+2], byteorder='big')
			offset += 2

			if len(app_layer) < offset + topic_len:
				return None  # app_layer too small
			topic = app_layer[offset:offset+topic_len].decode("utf-8")
			offset += topic_len

		payload = []
		if MQTTMessageType.has_payload(MQTTMessageType(header["control_header_type"])):
			payload_len = 2 + msg_len - offset # 2 first bytes header (always present)

			if len(app_layer) < offset +  payload_len:
				return None  # app_layer too small

			payload = app_layer[offset:offset+payload_len].decode("utf-8")
			if payload is None:
				payload = []

		return ["mqtt", header, topic, payload]

	def decode_connect_variable_header(self, header, app_layer, offset):
		connect_variable_header = {}
		offset = offset

		# Protocol Name

		if len(app_layer) < offset + 2:
			return None  # app_layer too small
		protocol_name_length = int.from_bytes(app_layer[offset:offset + 2],
											  byteorder='big')  # maybe change to little here (not sure)
		offset += 2

		if len(app_layer) < offset + protocol_name_length:
			return None  # app_layer too small
		connect_variable_header["protocol_name"] = app_layer[offset:offset + protocol_name_length].decode("utf-8")
		offset += protocol_name_length

		# Protocol version

		if len(app_layer) < offset + 1:
			return None  # app_layer too small
		connect_variable_header["protocol_version"] = app_layer[offset]
		offset += 1

		# Connect flags

		flag_byte = app_layer[offset]
		offset += 1

		connect_variable_header["flags"] = {}
		connect_variable_header["flags"]["user_name_flag"] = flag_byte & 128
		connect_variable_header["flags"]["password_flag"] = flag_byte & 64
		connect_variable_header["flags"]["will_retain"] = flag_byte & 32
		connect_variable_header["flags"]["will_qos"] = flag_byte & 24
		connect_variable_header["flags"]["will_flag"] = flag_byte & 4
		connect_variable_header["flags"]["clean_start"] = flag_byte & 2
		connect_variable_header["flags"]["reserved"] = flag_byte & 1

		# Keep Alive

		if len(app_layer) < offset + 2:
			return None  # app_layer too small
		connect_variable_header["keep_alive"] = int.from_bytes(app_layer[offset:offset + 2], byteorder='big')  # maybe change to little here (not sure)
		offset += 2

		# connect properties
		# TODO

		header["connect_variable_header"] = connect_variable_header

		return offset

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
	def update_packet_state(self, packet, packet_state):
		if self.is_unsubscribe_packet(packet):
			packet_state.remove_subscription(packet)
		elif self.is_disconnect_packet(packet):
			# if disconnected, client unsubscribe from all topics, this behavior can be changed
			packet_state.remove_client_subscriptions(packet)
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

	@classmethod
	def has_type(cls, type):
		return type in cls._value2member_map_

	@classmethod
	def has_packet_identifier(cls, type, qos):
		condition1 = type in [cls.PUBACK, cls.PUBREC, cls.PUBREL, cls.PUBCOMP, cls.SUBSCRIBE, cls.SUBACK, cls.UNSUBSCRIBE, cls.UNSUBACK]
		condition2 = type == cls.PUBLISH and qos > 0

		return condition1 or condition2

	@classmethod
	def has_topic(cls, type):
		return type in [cls.PUBLISH, cls.SUBSCRIBE]

	@classmethod
	def has_payload(cls, type):
		return type in [cls.CONNECT, cls.PUBLISH, cls.SUBSCRIBE, cls.SUBACK, cls.UNSUBSCRIBE, cls.UNSUBACK]