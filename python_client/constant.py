from enum import Enum

MAX_PAYLOAD = 1024


class ACTION(Enum):
    ADD = "add"
    REMOVE = "rm"


class CODE(Enum):
    C_PID = 0
    ADD_RULE = 1
    RM_RULE = 2
    ENABLE_RULE = 3
    DISABLE_RULE = 4
    ADD_RELATION = 5
    ADD_BROKER_RELATION = 6


class CONSTRAINT(Enum):
    NO_CONTEXT = "/"
    SUBJECT = "subject"
    INT = "int"
    STR = "str"
    TIME = "time"

class I_CONSTRAINT(Enum):
    SUBJECT = 0
    INT = 1
    STR = 2
    TIME = 3

class D_CONSTRAINT(Enum):
    TIME = 3

class M_TYPE(Enum):
    BROKER = "broker"
    PUB = "pub"
    SUB = "sub"


class T_TYPE(Enum):
    RULES = "rules"
    RELATIONS = "relations"


class POLICY(Enum):
    DENY = "deny"
    ALLOW = "allow"


class I_POLICY(Enum):
    DENY = 0
    ALLOW = 1
