import argparse
import signal
from threading import Thread

import pyximport  # This is part of Cython

pyximport.install()

from client.handler import Handler
from client.parser import Parser
from nfqueue.handling_queue import HandlingQueue
from context.input import ContextInput
from context.context import Context
from nfqueue.constraint_mapping import ConstraintMapping

parser = argparse.ArgumentParser()

parser.add_argument("--input", type=str, default=None)
parser.add_argument('--dev', dest='dev', action='store_true')
parser.add_argument('--no-dev', dest='dev', action='store_false')
parser.set_defaults(dev=True)
args = parser.parse_args()

if __name__ == "__main__":
    parser = Parser(args.input)

    if parser.err:
        print(parser.err)
        exit(1)

    constraint_mapping = ConstraintMapping()
    handling_queue = HandlingQueue(constraint_mapping)

    handler = Handler(handling_queue, constraint_mapping, args.dev)
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
