import signal
import threading

import Pyro4

from daemon.client_handlers import ClientHandlers, stop_client_handlers

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(ClientHandlers())
ns.register("ClientHandlers", uri)

daemon_thread = threading.Thread(target=daemon.requestLoop, args=())
print("Daemon ready")
daemon_thread.start()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    stop_client_handlers()
    daemon.close()
    daemon_thread.join()
    # sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
