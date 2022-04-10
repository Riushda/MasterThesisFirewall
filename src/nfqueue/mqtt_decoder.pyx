class MQTTDecoder:

	# MQTT layer
	# Remark : msg_len is the length of the remaining fields (not counting itself)
	#  _______________________________________________________________________________________
	# |        |         |           |                   |                                    |
	# | header | msg_len | topic_len |      topic        |              payload               |
	# | 1 byte | 1 byte  |  2 bytes  | topic_len byte(s) |  (msg_len - 2 - topic_len) byte(s) |
	# |________|_________|___________|___________________|____________________________________|

	def __init__(self):
		self.port = 1883
		self.MQTT_PUBLISH = 48

	def decode(self, app_layer):

		control_header = app_layer[0]

		if control_header==self.MQTT_PUBLISH :

			msg_len : int = app_layer[1]
			topic_len : int = int.from_bytes(app_layer[2:4], byteorder='big')

			offset = 4

			topic = app_layer[offset:offset+topic_len].decode("utf-8")
			offset += topic_len

			payload_len = msg_len - 2 - topic_len
			payload = app_layer[offset:offset+payload_len].decode("utf-8")

			return ["mqtt", control_header, topic, payload]

		return None

	def is_pull_packet(self, packet):
		return False # mqtt is push only