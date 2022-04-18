import signal
from threading import Thread

import pyximport  # This is part of Cython

pyximport.install()

from client.handler import Handler
from client.parser import Parser
from nfqueue.handling_queue import HandlingQueue
from context.input import ContextInput
from context.context import Context

if __name__ == "__main__":
    parser = Parser("input.json")

    handling_queue = HandlingQueue()

    handler = Handler(handling_queue)
    handler.add_parser(parser)

    handling_queue_thread = Thread(target=handling_queue.run)
    handling_queue_thread.start()

    context_input = ContextInput(handler)
    context = Context(handling_queue.packet_queue, context_input)

    context_thread = Thread(target=context.run)
    context_thread.start()


    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        handling_queue.stop()
        handling_queue_thread.join()
        context.stop()
        context_thread.join()


    signal.signal(signal.SIGINT, signal_handler)
