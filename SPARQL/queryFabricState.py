from enum import Enum


class QueryFabricState(Enum):
    INIT = 1
    PREFIX = 2
    SELECT = 3
    WHERE = 4
    ORDER_BY = 5
    BY = 6
    LIMIT = 7
    OFFSET = 8
    FILTER = 9
    BOUND = 10
    ERROR = 11
    FUNCTION_END = 12
    GRAPH_END = 13
    WHERE_END = 14
    OPTIONAL = 15
    SUBJECT = 16
    PREDICATE = 17
    OBJECT = 18
    GRAPH_START = 19
    OPTIONAL_END = 20
    UNION = 21
    UNION_END = 22
    FILTER_END = 23
    LEFT_OPERAND = 24
    OPERATOR = 25
    RIGHT_OPERAND = 26
    LOGICAL_AND = 27
    LOGICAL_OR = 28
    LOGICAL_UNKNOWN = 29
    NEGATION = 30
    END = 100
