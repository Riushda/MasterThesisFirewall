import signal
from threading import Thread

import pyximport  # This is part of Cython

pyximport.install()

from client.handler import Handler
from client.parser import JsonParser
from nfqueue.handling_queue import HandlingQueue

if __name__ == "__main__":
    parser = JsonParser("input.json")
    # print(parser)

    handling_queue = HandlingQueue()
    labels = {}
    members = {}
    relations = {}
    triggers = {}

    handler = Handler(handling_queue.constraint_mapping, handling_queue.packet_handler, labels,
                      members, relations, triggers)
    handler.add_parser(parser)

    handling_queue_thread = Thread(target=handling_queue.run)
    handling_queue_thread.start()


    # context_thread = Thread(target=context.run,
    #                        args=(handling_queue.packet_queue, pub_list, sub_list, broker_list, relations),
    #                        daemon=True)
    # context_thread.start()

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        handling_queue.stop()
        handling_queue_thread.join()
        # context_thread.join()


    signal.signal(signal.SIGINT, signal_handler)