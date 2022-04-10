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
		self.port = 5683

	def decode(self, app_layer):

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

		if header["TKL"] > 0:
			header["token"] = int(buffer[32:32+header["TKL"]*8], 2)
			offset += header["TKL"]*8

		# handle options

		header["options"] = {"host": "", "port": "", "path": [], "args": []}

		previous_delta = 0
		while offset<len(buffer) and int(buffer[offset:offset+8], 2)!=255:

			option_delta = int(buffer[offset:offset+4], 2)
			offset += 4

			delta = option_delta + previous_delta
			previous_delta = delta

			length = int(buffer[offset:offset+4], 2)
			offset += 4

			# extended delta if any
			if option_delta == 13 or option_delta==14:
				delta_size = delta - 12
				delta = int(buffer[offset:offset+delta_size*8], 2) + delta
				offset += delta_size*8
			elif option_delta==15:
				return None # error, message not valid

			# extended length if any
			if length==13:
				length = int(buffer[offset:offset + 8], 2) + 13
				offset += 8
			elif length==14:
				length = int(buffer[offset:offset + 16], 2) + 269
				offset += 16
			elif length==15:
				return None # error, message not valid

			offset += self.handle_option(header["options"], app_layer, int(offset/8), delta, length)

		offset += 8 # skip the 11111111 byte marker

		payload = None

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

	def is_pull_packet(self, packet):
		return False # mqtt is push only

class CoAPDelta(MultiValueEnum):
	RESERVED = 0, 128, 132, 136, 140
	IF_MATCH = 1
	URI_HOST = 3
	ETAG = 4
	IF_NONE_MATCH = 5
	OBSERVE = 6, 10 # 6 is observer in the coapthon library, 10 is lifetime option (see https://tools.ietf.org/id/draft-ietf-core-observe-01.html#option)
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

# for methods code :
# https://datatracker.ietf.org/doc/html/rfc7252#section-12.1.1 and https://datatracker.ietf.org/doc/html/rfc7252#section-12.1.2
# for responses code :
# https://tools.ietf.org/id/draft-ietf-core-coap-12.html#coap-code-registry-methods and https://tools.ietf.org/id/draft-ietf-core-coap-12.html#coap-code-registry-responses
class CoAPCode(Enum):

	# Request code
	GET = 1 # 0.01
	POST = 2 # 0.02
	PUT = 3 # 0.03
	DELETE = 4 # 0.04

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

class CoAPType(Enum):
	CONFIRMABLE = 0 # CON
	NON_CONFIRMABLE = 1 # NON
	ACKNOWLEDGMENT = 2 # ACK
	RESET = 3 # RST