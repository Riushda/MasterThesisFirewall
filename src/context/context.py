from _queue import Empty
from multiprocessing import Queue

import schedule
from transitions import MachineError

from context.input import ContextInput
from context.network import NetworkContext
from context.network import SelfLoopException
from context.schedule_thread import ScheduleThread
from context.triggers import Triggers
from context.utils import is_float, get_device_name, get_transition_trigger, add_relations_jobs
from nfqueue.abstract_packet import AbstractPacket


class Context:
    def __init__(self, packet_queue: Queue, context_input: ContextInput):
        self.network_context: NetworkContext = NetworkContext(context_input)
        self.packet_queue = packet_queue
        self.members = context_input.members
        self.categorization = context_input.categorization
        self.triggers = Triggers(context_input.triggers, self.network_context)
        self.keep_running = True

        self.schedule_thread = ScheduleThread(schedule)
        add_relations_jobs(context_input, self.schedule_thread)
        self.schedule_thread.start()

    def run(self):
        # self.network_context.draw_fsm()

        while self.keep_running:
            try:
                packet: AbstractPacket = self.packet_queue.get(block=True, timeout=1)

                for content in packet.content:
                    device = get_device_name(packet.src, self.members)
                    self.update_context(device, content)
                    # self.network_context.show_current_state()
                    # self.network_context.draw_fsm()

            except Empty:
                pass

    def stop(self):
        self.schedule_thread.stop()
        self.keep_running = False

    def update_context(self, device, packet_data):
        try:
            if device is None:
                print("Context log: Unknown publisher")
                return False

            if packet_data[0] not in self.members[device].fields:
                return False

            field = device + "." + packet_data[0]

            value = packet_data[1]
            if is_float(value):
                value = float(value)

            if self.categorization.has_mapping(field):
                value = self.categorization.map(field, value)

            trigger = get_transition_trigger(field, value)

            try:
                self.network_context.trigger(trigger, data=(field, value))
            except MachineError as e:
                if self.network_context.self_loop((field, value)):
                    raise SelfLoopException()
                else:
                    # print("Context log: MachineError - " + str(e))
                    return False

            except AttributeError as e:
                # print("Context log: AttributeError - " + str(e))
                return False

        except SelfLoopException:
            print("Context log: Self loop")
            return False

        return True
