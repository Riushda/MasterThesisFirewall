import signal
import threading
from threading import Thread

import Pyro4
import pyximport  # This is part of Cython

pyximport.install()

from context import context
from archive.client_handler import Handler, stop_client_handler
from nfqueue.handling_queue import HandlingQueue

handling_queue = HandlingQueue()

# This is an example to add an entry to the mapping

# c1 = Constraint(ConstraintType.INT.value, "temp", [[5, 10], [15, 20]])
# c2 = Constraint(ConstraintType.STR.value, "name", ["alice", "bob"])
# constraint_list = [c1, c2]
# mapping_entry = MappingEntry("test", constraint_list, Policy.ACCEPT.value)
# constraint_mapping.add_mapping("0", mapping_entry)

pub_list = {}
sub_list = {}
broker_list = {}
relations = []

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(
    Handler(handling_queue.constraint_mapping, handling_queue.packet_handler, pub_list, sub_list, broker_list,
            relations))
ns.register("ClientHandlers", uri)

daemon_thread = threading.Thread(target=daemon.requestLoop, args=())
print("Daemon ready")
daemon_thread.daemon = True
daemon_thread.start()

handling_queue_thread = Thread(target=handling_queue.run, daemon=True)
handling_queue_thread.daemon = True
handling_queue_thread.start()

context_thread = Thread(target=context.run,
                        args=(handling_queue.packet_queue, pub_list, sub_list, broker_list, relations),
                        daemon=True)
context_thread.daemon = True
context_thread.start()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    stop_client_handler()
    daemon.close()
    daemon_thread.join()
    handling_queue.stop()
    handling_queue_thread.join()
    # context_thread.join()


signal.signal(signal.SIGINT, signal_handler)
