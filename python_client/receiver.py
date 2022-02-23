import struct
import ipaddress
import re

def receive(netlink, event):

	while not event.is_set() :

		data = netlink.recv_msg()

		if data:
			msg_len, msg_type, flags, seq, pid = struct.unpack("=LHHLL", data[:16])
			
			buffer = bytearray(data[16:msg_len])

			# decode network layer

			src = bytes_to_int(buffer[0:4])
			dst = bytes_to_int(buffer[4:8])
			sport = bytes_to_int(buffer[8:10])
			dport = bytes_to_int(buffer[10:12])

			# decode application layer

			topic_len = buffer[12]

			topic = buffer[13:13+topic_len].decode()

			payload_len = buffer[13+topic_len]

			payload = buffer[13+topic_len+1:13+topic_len+1+payload_len].decode()

			print("src: "+int_to_ip_str(src))
			print("dst: "+int_to_ip_str(dst))
			print("sport: "+str(sport))
			print("dport: "+str(dport))

			print(topic)
			print(payload)

			pattern = re.compile('\??(\w+)=(\w+)&?', re.IGNORECASE)
			groups = pattern.findall(payload)

			for group in groups :
				field = group[0]
				value = group[1]
				print(field)
				print(value)

			
	print("receiver thread ended")

def bytes_to_int(bytes : bytearray):

	integer = int.from_bytes(bytes, byteorder='little', signed=False)

	return integer

def int_to_ip_str(integer):
	return str(ipaddress.ip_address(integer))