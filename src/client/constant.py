from enum import Enum


class Action(Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class Policy(Enum):
    DROP = "drop"
    ACCEPT = "accept"
    DEFAULT = "default"


class FieldType(Enum):
    DEC = "decimal"
    STR = "string"


class TriggerType(Enum):
    TIME = "time"
    FIELD = "field"
