from daemon.rule import Rule
from utils.constant import *


class Relation:
    def __init__(self, first: Rule, second: Rule = None, constraints: list = [], mark: str = "0"):
        self.has_broker = 0
        if second:
            self.has_broker = 1
        self.first = first
        self.second = second
        self.constraints = constraints
        self.mark = mark
        self.jobs = []

    def __str__(self):
        constraint_str = ""
        for c in self.constraints:
            constraint_str += f"{c} ; "
        if self.second:
            return f"{self.first} ~ {self.second} \n {constraint_str}"
        else:
            return f"{self.first} \n {constraint_str}"

    def add_jobs(self, api, schedule, task):
        for c in self.constraints:
            if c.c_type == ConstraintType.TIME.value:
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
