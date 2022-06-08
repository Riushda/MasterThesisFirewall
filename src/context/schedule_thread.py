"""
This class defines the scheduling thread responsible for activating and deactivating the relations depending on the time
of day.
"""

import threading
import time


class ScheduleThread:
    def __init__(self, schedule):
        self.thread = threading.Thread(target=self.thread_function, args=())
        self.keep_running = True
        self.schedule = schedule
        self.jobs = []

    def thread_function(self):
        while self.keep_running:
            self.schedule.run_pending()
            time.sleep(1)

    def start(self):
        self.thread.start()

    def stop(self):
        self.keep_running = False
        for job in self.jobs:
            self.schedule.cancel_job(job)
        self.thread.join()
