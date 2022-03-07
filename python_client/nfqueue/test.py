from threading import Thread
from multiprocessing import Queue
import time
from lib import nf_queue
from lib import abstract_packet
import sys
sys.path.append('../')
from context import context

'''
nf_queue.constraint_list.add_constraint(2,0,"temp", None)
nf_queue.constraint_list.add_constraint(1,1,"memory_usage", [23, 40])
nf_queue.constraint_list.add_constraint(0,2,"update", ["BIOS", "ubuntu"])
#nf_queue.constraint_list.show()

nf_queue.constraint_list.del_constraint(1)
#nf_queue.constraint_list.show()'''

#packet = abstract_packet.AbstractPacket(2, "192.168.0.104", "192.168.1.230", 55777, 22, "hello", [("field1", "value1"), ("value2"), ("field3", "value3")])
#print(packet)

# start threads here

packet_queue = Queue()

thread1 = Thread(target = nf_queue.run, args=(packet_queue,), daemon=True)
thread1.start()

thread2 = Thread(target = context.run, args=(packet_queue,), daemon=True)
thread2.start()

while(True):
	time.sleep(5)
