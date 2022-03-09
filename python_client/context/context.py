from multiprocessing import Queue
import Pyro4

daemon = Pyro4.Proxy("PYRONAME:handlers")
'''
daemon functions that will be called 

daemon.add_member(name, str_ip, str_port, type)
daemon.remove_member(name, type)
daemon.add_relation(pub, sub, broker, policy, context)
daemon.remove_relation(index)
daemon.add_rule(src, sport, dst, dport, policy)
daemon.remove_rule(index)
'''

def init() :
	global network_state
	network_state = {}

def run(packet_queue : Queue, pub_list, sub_list, broker_list, relations):

	init()

	while True :
		try:
			packet = packet_queue.get(block=True, timeout=10)
			print(packet)
		except:
			print("No packet within timeout seconds")

		
		state_src = network_state[packet.src]
		state_dst = network_state[packet.dst]


