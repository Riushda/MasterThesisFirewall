from client.member import Member


class Rule:
    def __init__(self, src: Member, dst: Member, handle: int):
        self.src = src
        self.dst = dst
        self.handle = handle

    def __str__(self):
        return f"{self.src} -> {self.dst}"
