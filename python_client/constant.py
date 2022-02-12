from enum import Enum

MAX_PAYLOAD = 1024


class ACTION(Enum):
    ADD = "add"
    REMOVE = "rm"


class COMMAND(Enum):
    MEMBER = "member"
    RELATION = "relation"
    RULE = "rule"
    SHOW = "show"


class CODE(Enum):
    PID = 0
    ADD_RELATION = 1
    RM_RELATION = 2
    ENABLE_RELATION = 3
    DISABLE_RELATION = 4


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
