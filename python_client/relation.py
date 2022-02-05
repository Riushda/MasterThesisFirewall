from rule import Rule
from constant import *


class Relation():
    def __init__(self, first: Rule, second: Rule = None, context: list = []):
        self.has_broker = 0
        if(second):
            self.has_broker = 1
        self.first = first
        self.second = second
        self.context = context
        self.jobs = []

    def __str__(self):
        if(self.second):
            return f"{self.first} ~ {self.second}"
        else:
            return f"{self.first}"

    def add_jobs(self, netlink, schedule, task):
        for c in self.context:
            if(c.type == I_CONSTRAINT.TIME.value):
                for v in c.values:
                    job = schedule.every().day.at(v[0]).do(
                        task, netlink, CODE.ENABLE_RULE.value, self.first.index)
                    self.jobs.append(job)

                    job = schedule.every().day.at(v[1]).do(
                        task, netlink, CODE.DISABLE_RULE.value, self.first.index)
                    self.jobs.append(job)

    def cancel_jobs(self, schedule):
        for j in self.jobs:
            schedule.cancel_job(j)

    def add_to_kernel(self, netlink):
        netlink.send_msg(CODE.ADD_RELATION.value, self.to_bytes())

    def rm_from_kernel(self, netlink):
        netlink.send_msg(CODE.RM_RELATION.value, self.has_broker.to_bytes(1, 'little') +
                         self.first.index.to_bytes(2, 'little'))

    def to_bytes(self):
        s_constraints = []
        for x in range(0, len(self.context)):
            if(not self.context[x].type in D_CONSTRAINT._value2member_map_):
                s_constraints.append(x)

        buffer = bytearray()

        buffer += self.has_broker.to_bytes(1, 'little')
        buffer += self.first.to_bytes()

        if(self.second):
            buffer += self.second.to_bytes()
        buffer += len(s_constraints).to_bytes(1, 'little')

        for x in s_constraints:
            buffer += self.context[x].to_bytes()

        return buffer
