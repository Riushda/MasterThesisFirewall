import signal
import threading
from multiprocessing import Queue
from threading import Thread

import Pyro4
import pyximport  # This is part of Cython

pyximport.install()

from context import context
from client.handlers import Handlers, stop_client_handlers
from nfqueue import handling_queue
from nfqueue.constraint_mapping import ConstraintMapping

constraint_mapping = ConstraintMapping()  # This structure contains the constraints for each mark

# This is an example to add an entry to the mapping

# c1 = Constraint(ConstraintType.INT.value, "temp", [[5, 10], [15, 20]])
# c2 = Constraint(ConstraintType.STR.value, "name", ["alice", "bob"])
# constraint_list = [c1, c2]
# mapping_entry = MappingEntry("test", constraint_list, Policy.ACCEPT.value)
# constraint_mapping.add_mapping("0", mapping_entry)

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Handlers(constraint_mapping))
ns.register("ClientHandlers", uri)

daemon_thread = threading.Thread(target=daemon.requestLoop, args=())
print("Daemon ready")
daemon_thread.start()

packet_queue = Queue()

thread1 = Thread(target=handling_queue.run, args=(packet_queue, constraint_mapping,), daemon=True)
thread1.start()

relations = []
broker_list = {}
pub_list = {}
sub_list = {}

thread2 = Thread(target=context.run, args=(packet_queue, pub_list, sub_list, broker_list, relations), daemon=True)
thread2.start()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    stop_client_handlers()
    daemon.close()
    daemon_thread.join()
    # sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
