from utils.constant import *


class Relation:
    def __init__(self, subject: str, mark: int, first: list, second: list = None, constraints: list = None):
        self.subject = subject
        self.mark = mark
        self.first = first
        self.second = second
        self.constraints = constraints
        self.jobs = []

    def add_jobs(self, api, schedule, task):
        for c in self.constraints:
            if c.f_type == TriggerType.TIME.value:
                for v in c.value:
                    job = schedule.every().day.at(v[0]).do(
                        task, api, Code.ENABLE_RELATION.value, self)
                    self.jobs.append(job)

                    job = schedule.every().day.at(v[1]).do(
                        task, api, Code.DISABLE_RELATION.value, self)
                    self.jobs.append(job)

    def cancel_jobs(self, schedule):
        for j in self.jobs:
            schedule.cancel_job(j)