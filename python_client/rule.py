from constant import *
from member import Member


class Rule():
    def __init__(self, src: Member, dst: Member, index, policy=1, is_relation=True):
        self.src = src
        self.dst = dst
        self.policy = policy
        self.index = index
        self.is_relation = is_relation

    def __str__(self):
        return f"{self.src} -> {self.dst} {self.policy}"

    def to_bytes(self):
        buffer = bytearray()
        src_buffer = self.src.to_bytes()
        dst_buffer = self.dst.to_bytes()

        buffer = src_buffer + dst_buffer
        buffer += I_POLICY[self.policy.upper()].value.to_bytes(1, 'little')
        buffer += self.index.to_bytes(2, 'little')

        return buffer
