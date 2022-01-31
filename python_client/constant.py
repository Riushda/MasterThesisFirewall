from enum import Enum

MAX_PAYLOAD = 1024


class ACTION(Enum):
    ADD = "add"
    REMOVE = "rm"


class M_TYPE(Enum):
    BROKER = "broker"
    PUB = "pub"
    SUB = "sub"

class T_TYPE(Enum):
    RULES = "rules"
    RELATIONS = "relations"