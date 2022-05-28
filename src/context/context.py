import time
from _queue import Empty
from multiprocessing import Queue
import threading

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

        self.avg_queue_size = 0
        self.count_queue_size = 0
        self.avg_update_time = 0
        self.count_update = 0

        self.measure_thread = None

    def measure(self):
        while self.count_update < 10000 and self.keep_running:
            time.sleep(0.05)
            queue_size = self.packet_queue.qsize()
            self.avg_queue_size += queue_size
            self.count_queue_size += 1

        print("All packets fed to context !")

    def run(self):
        # self.network_context.draw_fsm()

        while self.keep_running:
            try:
                packet: AbstractPacket = self.packet_queue.get(block=True, timeout=1)

                if self.count_update == 0:
                    self.measure_thread = threading.Thread(target=self.measure, args=())
                    self.measure_thread.start()

                for content in packet.content:
                    device = get_device_name(packet.src, self.members)
                    start = time.time_ns()
                    self.update_context(device, content)
                    end = time.time_ns()
                    self.avg_update_time += end - start
                    self.count_update += 1
                    # self.network_context.show_current_state()
                    # self.network_context.draw_fsm()

            except Empty:
                pass

    def stop(self):
        print(self.count_update)
        self.schedule_thread.stop()
        print("avg queue size : "+str(self.avg_queue_size/self.count_queue_size))
        print("avg update time : "+str(self.avg_update_time/(self.count_update*1000000))+" ms")
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
