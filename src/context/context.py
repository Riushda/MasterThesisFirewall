from _queue import Empty
from multiprocessing import Queue

from transitions import MachineError

from context.abstract_rule import AbstractRule
from context.input import ContextInput
from context.network import NetworkContext, get_transition_trigger
from context.network import SelfLoopException
from context.utils import is_float, get_device_name, get_relations_jobs, cancel_relations_jobs
from nfqueue.abstract_packet import AbstractPacket

from context.schedule_thread import ScheduleThread
import schedule
import threading


class Context:
    def __init__(self, packet_queue: Queue, context_input: ContextInput):
        self.network_context = NetworkContext(context_input)
        self.packet_queue = packet_queue
        self.members = context_input.members
        self.categorization = context_input.categorization
        self.abstract_rules = AbstractRule(context_input.abstract_rules, self.network_context,
                                           context_input.handler)
        self.keep_running = True

        s_mutex = threading.Lock()
        self.schedule_thread = ScheduleThread(s_mutex, schedule)
        self.schedule_thread.start()
        self.jobs = get_relations_jobs(context_input.time_intervals, context_input.handler, self.schedule_thread)

    def run(self):
        self.network_context.draw_fsm()

        while self.keep_running:
            try:
                packet: AbstractPacket = self.packet_queue.get(block=True, timeout=3)

                for content in packet.content:
                    device = get_device_name(packet.src, self.members)
                    self.update_context(device, content)
                    self.network_context.show_current_state()
                    self.network_context.draw_fsm()

            except Empty:
                pass

    def stop(self):
        cancel_relations_jobs(self.jobs, self.schedule_thread)
        self.schedule_thread.stop()
        self.keep_running = False

    def update_context(self, device, packet_data):
        try:
            if device is None:
                print("Unknown publisher !")
                return

            field = device + "." + packet_data[0]

            value = packet_data[1]
            if is_float(value):
                value = float(value)

            if self.categorization.has_mapping(field):
                value = self.categorization.map(field, value)

            print(field, value)
            trigger = get_transition_trigger(field, value)

            try:
                self.network_context.trigger(trigger, data=(field, value))
            except MachineError as e:
                if self.network_context.self_loop((field, value)):
                    raise SelfLoopException()
                else:
                    print("MachineError: " + str(e))
                    return False

            except AttributeError as e:
                print(str(e))
                return False

        except SelfLoopException:
            print("Self Loop")
            return False

        return True
