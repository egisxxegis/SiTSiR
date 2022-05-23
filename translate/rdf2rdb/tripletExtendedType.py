from enum import Enum


class TripletExtendedType(Enum):
    ONLY_URI = 0
    VAR_OBJECT = 1
    VAR_PREDICATE = 2
    VAR_PO = 3
    VAR_SUBJECT = 4
    VAR_SO = 5
    VAR_SP = 6
    VAR_SPO = 7
    UNKNOWN = 8
