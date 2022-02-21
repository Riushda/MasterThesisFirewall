import struct

def receive(netlink, event):

	while not event.is_set() :

		data = netlink.recv_msg()

		if data:
			msg_len, msg_type, flags, seq, pid = struct.unpack("=LHHLL", data[:16])
			print("msg_len = "+str(msg_len))
			print("msg_type = "+str(msg_type))
			print("flags = "+str(flags))
			print("seq = "+str(seq))
			print("pid = "+str(pid))
			print(data[16:msg_len])

	
	print("FINISH")