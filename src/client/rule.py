from client.member import Member
from utils.constant import *


class Rule:
    def __init__(self, src: Member, dst: Member, handle: int, policy=Policy.ACCEPT.value, is_relation=True):
        self.src = src
        self.dst = dst
        self.policy = policy
        self.handle = handle
        self.is_relation = is_relation

    def __str__(self):
        return f"{self.src} -> {self.dst} {self.policy}"
