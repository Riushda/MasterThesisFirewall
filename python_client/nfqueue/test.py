from threading import Thread
from multiprocessing import Queue
import time
import sys
sys.path.append('../') # not needed when running from parent directory
from context import context

import pyximport   # This is part of Cython
pyximport.install()
import abstract_packet
import nf_queue

nf_queue.constraint_list.add_constraint(2, 0, "temp", None)
nf_queue.constraint_list.add_constraint(1, 1, "memory_usage", [23, 40])
nf_queue.constraint_list.add_constraint(0, 2, "update", ["BIOS", "ubuntu"])
# nf_queue.constraint_list.show()

# nf_queue.constraint_list.del_constraint(1)
# nf_queue.constraint_list.show()

# packet = abstract_packet.AbstractPacket(2, "192.168.0.104", "192.168.1.230", 55777, 22, "hello", [("field1", "value1"), ("value2"), ("field3", "value3")])
# print(packet)

# start threads here

packet_queue = Queue()

thread1 = Thread(target=nf_queue.run, args=(packet_queue,), daemon=True)
thread1.start()

relations = []
broker_list = {}
pub_list = {}
sub_list = {}

thread2 = Thread(target=context.run, args=(packet_queue, pub_list, sub_list, broker_list, relations), daemon=True)
thread2.start()

while (True):
    time.sleep(5)
