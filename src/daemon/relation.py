from daemon.rule import Rule
from utils.constant import *


class Relation:
    def __init__(self, first: Rule, second: Rule = None, context: list = []):
        self.has_broker = 0
        if second:
            self.has_broker = 1
        self.first = first
        self.second = second
        self.context = context
        self.jobs = []

    def __str__(self):
        if self.second:
            return f"{self.first} ~ {self.second}"
        else:
            return f"{self.first}"

    def add_jobs(self, api, schedule, task):
        for c in self.context:
            if c.type == IntegerConstraint.TIME.value:
                for v in c.values:
                    job = schedule.every().day.at(v[0]).do(
                        task, api, Code.ENABLE_RELATION.value, self)
                    self.jobs.append(job)

                    job = schedule.every().day.at(v[1]).do(
                        task, api, Code.DISABLE_RELATION.value, self)
                    self.jobs.append(job)

    def cancel_jobs(self, schedule):
        for j in self.jobs:
            schedule.cancel_job(j)
