from netfilterqueue import NetfilterQueue, Packet
from scapy.layers.inet6 import IPv6
from scapy.layers.inet import IP, TCP, UDP
import scapy.all as scapy
from multiprocessing import Queue

from lib import protocol
from lib import abstract_packet
from lib import data_constraint

constraint_list = data_constraint.ConstraintList()
packet_queue = None

def handle_packet(pkt : Packet):

	mac_src = pkt.get_hw() # src mac_address
	#print(mac_src.hex(":"))

	packet = IP(pkt.get_payload())
	#print(packet.payload.layers()) => show all layers of packet

	src = None
	dst = None
	sport = None
	dport = None

	if packet.haslayer(IP) :
		src=packet[IP].src
		dst=packet[IP].dst
	elif packet.haslayer(IPv6) :
		src=packet[IPv6].src
		dst=packet[IPv6].dst
	else :
		# should never reach there because ethernet packets are not hooked
		pkt.accept()
		return

	#print(" IP src " + str(src) + " IP dst " + str(dst))

	if packet.haslayer(TCP):
		sport=packet[TCP].sport
		dport=packet[TCP].dport
		#print(" TCP sport " + str(sport) + " TCP dport " + str(dport))

	elif packet.haslayer(UDP) :
		sport=packet[UDP].sport
		dport=packet[UDP].dport
		#print(" UDP sport " + str(udp_sport) + " UDP dport " + str(udp_dport))
	else :
		print("unknown transport layer protocol")

	if packet.haslayer(scapy.Raw) :
		app_layer = packet[scapy.Raw].load
		
		decoded = protocol.decode_packet(dport, app_layer)

		if decoded :
			# if protocol layer has been successfully decoded 

			mark = pkt.get_mark()

			abstract_pkt = abstract_packet.AbstractPacket(mark, src, dst, sport, dport, decoded[0], decoded[1])

			match = constraint_list.match_packet(abstract_pkt)

			if not match:
				pkt.drop()
				return

			packet_queue.put(abstract_pkt)

	pkt.accept()

def run(queue : Queue) :
	global packet_queue
	packet_queue = queue

	nfqueue = NetfilterQueue()
	nfqueue.bind(0, handle_packet)
	try :
		nfqueue.run()
	except KeyboardInterrupt :
		print('bye')
		nfqueue.unbind()
		exit(0)