from aenum import MultiValueEnum
from enum import Enum

class CoAPDecoder:

	# CoAP layer
	# see https://datatracker.ietf.org/doc/html/rfc7252 for more details
	#  0					            1                             2                             3
	#  0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5  6  7  8  9  0  1
	# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
	# | Ver |  T  |    TKL   |           Code         |                Message ID                    |
	# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
	# | Token (if any) ...
	# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
	# | Options (if any) ...
	# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
	# |1  1  1  1  1  1  1  1| Payload (if any) ...
	# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
	#
	# Option header before each option
	#     0   1   2   3   4   5   6   7
	#   +---------------+---------------+
	#   |               |               |
	#   |  Option Delta | Option Length |   1 byte
	#   |               |               |
	#   +---------------+---------------+
	#   \                               \
	#   /         Option Delta          /   0-2 bytes
	#   \          (extended)           \
	#   +-------------------------------+
	#   \                               \
	#   /         Option Length         /   0-2 bytes
	#   \          (extended)           \
	#   +-------------------------------+
	#   \                               \
	#   /                               /
	#   \                               \
	#   /         Option Value          /   0 or more bytes
	#   \                               \
	#   /                               /
	#   \                               \
	#   +-------------------------------+

	def __init__(self):
		self.protocol_name = "coap"
		self.port = 5683

	def match_protocol(self, sport, dport):
		return sport == self.port or dport == self.port

	def decode(self, app_layer):

		if len(app_layer) < 3:
			return None # packet smaller than header size

		header = {}
		buffer = list(bin(int.from_bytes(app_layer, byteorder='big')))
		buffer = buffer[1:]
		buffer[0] = '0'
		buffer = "".join(buffer)

		header["Ver"] = int(buffer[0:2], 2)
		header["T"] = int(buffer[2:4], 2)
		header["TKL"] = int(buffer[4:8], 2)
		header["Code"] = int(buffer[8:16], 2)
		header["msg_id"] = int(buffer[16:32], 2)

		offset = 32

		if len(app_layer) < (offset/8) + header["TKL"]:
			return None # app_layer too small

		if header["TKL"] > 0:
			header["token"] = int(buffer[32:32+header["TKL"]*8], 2)
			offset += header["TKL"]*8

		# handle options

		header["options"] = {"host": "", "port": "", "path": [], "args": []}

		previous_delta = 0
		while offset<len(buffer) and int(buffer[offset:offset+8], 2)!=255:

			if len(app_layer) < (offset/8) + 1:
				return None  # app_layer too small

			option_delta = int(buffer[offset:offset+4], 2)
			offset += 4

			delta = option_delta + previous_delta
			previous_delta = delta

			length = int(buffer[offset:offset+4], 2)
			offset += 4

			# extended delta if any
			if option_delta == 13 or option_delta==14:
				delta_size = delta - 12

				if len(app_layer) < (offset / 8) + delta_size:
					return None  # app_layer too small

				delta = int(buffer[offset:offset+delta_size*8], 2) + delta
				offset += delta_size*8
			elif option_delta==15:
				return None # error, message not valid

			# extended length if any
			if length==13:
				if len(app_layer) < (offset / 8) + 1:
					return None  # app_layer too small

				length = int(buffer[offset:offset + 8], 2) + 13
				offset += 8
			elif length==14:
				if len(app_layer) < (offset / 8) + 2:
					return None  # app_layer too small

				length = int(buffer[offset:offset + 16], 2) + 269
				offset += 16
			elif length==15:
				return None # error, message not valid

			if len(app_layer) < (offset / 8) + length:
				return None  # app_layer too small

			offset += self.handle_option(header["options"], app_layer, int(offset/8), delta, length)

		offset += 8 # skip the 11111111 byte marker

		payload = []

		# handle payload
		if offset < len(buffer):
			payload = app_layer[int(offset/8):].decode("utf-8")

		return ["coap", header, '/'.join(header["options"]["path"]), payload]

	def handle_option(self, options, app_layer, offset, delta, length):
		try:
			if CoAPDelta(delta) == CoAPDelta.RESERVED:
				pass
			elif CoAPDelta(delta) == CoAPDelta.IF_MATCH:
				pass
			elif CoAPDelta(delta) == CoAPDelta.URI_HOST:
				pass
			elif CoAPDelta(delta) == CoAPDelta.ETAG:
				pass
			elif CoAPDelta(delta) == CoAPDelta.IF_NONE_MATCH:
				pass
			elif CoAPDelta(delta) == CoAPDelta.OBSERVE:
				options["observe"] = int.from_bytes(app_layer[offset:offset + length], byteorder='big')
				return length * 8

			elif CoAPDelta(delta) == CoAPDelta.URI_PORT:
				pass
			elif CoAPDelta(delta) == CoAPDelta.LOCATION_PATH:
				if options.get("location-path", None) is None:
					options["location-path"] = []

				options["location-path"].append(app_layer[offset:offset + length].decode("utf-8"))
				return length*8

			elif CoAPDelta(delta) == CoAPDelta.URI_PATH:
				options["path"].append(app_layer[offset:offset + length].decode("utf-8"))
				return length*8

			elif CoAPDelta(delta) == CoAPDelta.CONTENT_FORMAT:
				pass
			elif CoAPDelta(delta) == CoAPDelta.MAX_AGE:
				pass
			elif CoAPDelta(delta) == CoAPDelta.URI_QUERY:
				options["args"].append(app_layer[offset:offset + length].decode("utf-8"))
				return length*8

			elif CoAPDelta(delta) == CoAPDelta.ACCEPT:
				pass
			elif CoAPDelta(delta) == CoAPDelta.LOCATION_QUERY:
				pass
			elif CoAPDelta(delta) == CoAPDelta.PROXY_URI:
				pass
			elif CoAPDelta(delta) == CoAPDelta.PROXY_SCHEME:
				pass
			elif CoAPDelta(delta) == CoAPDelta.SIZE1:
				pass
		except ValueError as e:
			print(e)

		return 0

	# functions for pull packets

	def is_pull_packet(self, packet):
		return packet.header["options"].get("observe", None) is None

	def is_request(self, packet):
		return CoAPRequestCode.has_code(packet.header["Code"]) and \
			   (CoAPType(packet.header["T"]) == CoAPType.CONFIRMABLE or
				CoAPType(packet.header["T"]) == CoAPType.NON_CONFIRMABLE)

	def is_response(self, packet):

		response = CoAPResponseCode.has_code(packet.header["Code"])

		sync_response = response and CoAPType(packet.header["T"]) == CoAPType.ACKNOWLEDGMENT

		async_response = response and CoAPType(packet.header["T"]) == CoAPType.NON_CONFIRMABLE

		return sync_response or async_response

	def is_signaling(self, packet):
		return CoAPType(packet.header["T"]) in [CoAPType.ACKNOWLEDGMENT, CoAPType.RESET]

	def is_request_successful(self, packet, request_packet):
		request_code = CoAPRequestCode(request_packet.header["Code"])
		response_code = CoAPRequestCode(packet.header["Code"])

		successful_get = request_code == CoAPRequestCode.GET and CoAPResponseCode.is_get_successful(response_code)

		successful_post = request_code == CoAPRequestCode.POST and CoAPResponseCode.is_post_successful(response_code)

		successful_put = request_code == CoAPRequestCode.PUT and CoAPResponseCode.is_put_successful(response_code)

		successful_del = request_code == CoAPRequestCode.DELETE and CoAPResponseCode.is_del_successful(response_code)

		return successful_get or successful_post or successful_put or successful_del

	def get_msg_id(self, packet):
		return packet.header["msg_id"]

	# make further verification, specific to the protocol
	def match_request(self, packet, request_packet):
		if CoAPRequestCode(request_packet.header["Code"]) == CoAPRequestCode.GET:
			packet.subject = request_packet.subject # for get request, response doesn't have the path (needed because context is updated with response)

		return CoAPType(packet.header["T"]) == CoAPType.ACKNOWLEDGMENT and \
			   packet.header["token"] == request_packet.header["token"]

	# functions for push packets

	def is_push_packet(self, packet):
		return packet.header["options"].get("observe", None) is not None

	# make further verification, specific to the protocol
	def match_subscription(self, packet, subscription_packet):
		packet.subject = subscription_packet.subject # in coap, the push messages doesn't contain the path (needed because context is updated with response)
		return packet.header["token"] == subscription_packet.header["token"]

	# this can trigger function in the packet_state class depending on the type of the packet
	def ask_trigger(self, packet):
		return "None" # no trigger for the moment

# for methods code :
# https://datatracker.ietf.org/doc/html/rfc7252#section-12.1.1 and https://datatracker.ietf.org/doc/html/rfc7252#section-12.1.2
# for responses code :
# https://tools.ietf.org/id/draft-ietf-core-coap-12.html#coap-code-registry-methods and https://tools.ietf.org/id/draft-ietf-core-coap-12.html#coap-code-registry-responses
class CoAPRequestCode(Enum):

	# Request code
	GET = 1 # 0.01
	POST = 2 # 0.02
	PUT = 3 # 0.03
	DELETE = 4 # 0.04

	@classmethod
	def has_code(cls, code):
		return code in cls._value2member_map_

class CoAPResponseCode(Enum):
	# Response code
	CREATED = 65 # 2.01
	DELETED = 66 # 2.02
	VALID = 67 # 2.03
	CHANGED = 68 # 2.04
	CONTENT = 69 # 2.05
	BAD_REQUEST = 128 # 4.00
	UNAUTHORIZED = 129 # 4.01
	BAD_OPTION = 130 # 4.02
	FORBIDDEN = 131 # 4.03
	NOT_FOUND = 132 # 4.04
	METHOD_NOT_ALLOWED = 133 # 4.05
	NOT_ACCEPTABLE = 134 # 4.06
	PRECONDITION_FAILED = 140 # 4.12
	REQUEST_ENTITY_TOO_LARGE = 141 # 4.13
	UNSUPPORTED_CONTENT_FORMAT = 143 # 4.15
	INTERNAL_SERVER_ERROR = 160 # 5.00
	NOT_IMPLEMENTED = 161 # 5.01
	BAD_GATEWAY = 162 # 5.02
	SERVICE_UNAVAILABLE = 163 # 5.03
	GATEWAY_TIMEOUT = 164 # 5.04
	PROXYING_NOT_SUPPORTED = 165 # 5.05

	@classmethod
	def has_code(cls, code):
		return code in cls._value2member_map_

	@classmethod
	def is_get_successful(cls, code):
		return code in [cls.CONTENT, cls.VALID]

	@classmethod
	def is_post_successful(cls, code):
		return code in [cls.CREATED, cls.CHANGED, cls.DELETED]

	@classmethod
	def is_put_successful(cls, code):
		return code in [cls.CREATED, cls.CHANGED]

	@classmethod
	def is_del_successful(cls, code):
		return code == cls.CREATED

class CoAPType(Enum):
	CONFIRMABLE = 0 # CON
	NON_CONFIRMABLE = 1 # NON
	ACKNOWLEDGMENT = 2 # ACK
	RESET = 3 # RST

class CoAPDelta(MultiValueEnum):
	RESERVED = 0, 128, 132, 136, 140
	IF_MATCH = 1
	URI_HOST = 3
	ETAG = 4
	IF_NONE_MATCH = 5
	OBSERVE = 6, 10  # 6 is observer in the coapthon library, 10 is lifetime option (see https://tools.ietf.org/id/draft-ietf-core-observe-01.html#option)
	URI_PORT = 7
	LOCATION_PATH = 8
	URI_PATH = 11
	CONTENT_FORMAT = 12
	MAX_AGE = 14
	URI_QUERY = 15
	ACCEPT = 17
	LOCATION_QUERY = 20
	PROXY_URI = 35
	PROXY_SCHEME = 39
	SIZE1 = 60