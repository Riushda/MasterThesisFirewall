import threading
import time

from constant import *


class ScheduleThread():
    def __init__(self, s_mutex, schedule):
        self.thread = threading.Thread(target=self.thread_function, args=())
        self.keep_running = True
        self.k_mutex = threading.Lock()
        self.s_mutex = s_mutex
        self.schedule = schedule

    def thread_function(self):
        self.k_mutex.acquire()

        while self.keep_running:
            self.k_mutex.release()
            self.s_mutex.acquire()
            self.schedule.run_pending()
            self.s_mutex.release()
            time.sleep(1)
            self.k_mutex.acquire()

    def start(self):
        self.thread.start()

    def stop(self):
        self.k_mutex.acquire()
        self.keep_running = False
        self.k_mutex.release()
        self.thread.join()


def schedule_job(netlink, code, has_broker, index):

    data = bytearray()

    data += has_broker.to_bytes(1, 'little')
    data += index.to_bytes(2, 'little')

    netlink.send_msg(code, data)
