from email import policy
import member


class Rule():
    def __init__(self, source: member, destination: member, index, policy=1):
        self.src = source
        self.dst = destination
        self.policy = policy
        self.index = index

    def __str__(self):
        policy = "allow"
        if(self.policy == 0):
            policy = "deny"

        return f"{self.src} -> {self.dst} {policy}"

    def to_bytes(self):
        buffer = bytearray()
        src_buffer = self.source.to_bytes()
        dst_buffer = self.destination.to_bytes()

        buffer = src_buffer + dst_buffer
        buffer += self.policy.to_bytes(1, 'little')
        buffer += self.index.to_bytes(2, 'little')

        # buffer[0:3] = src_buffer[0:3]
        # buffer[4:7] = dst_buffer[0:3]
        # buffer[8:9] = src_buffer[5:6]
        # buffer[10:11] = dst_buffer[5:6]
        # buffer[12:12] = src_buffer[4:4]
        # buffer[13:13] = dst_buffer[4:4]
        # buffer[16:16] = src_buffer[7:7]
        # buffer[17:17] = dst_buffer[7:7]
