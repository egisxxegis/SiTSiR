from SPARQL.triplet import Triplet
from SPARQL.filter import Filter


class Graph:
    def __init__(self):
        self.is_optional = False
        self.is_union = False
        self.filter = Filter()

        self.parent = None
        self.child = None
        self.previous = None
        self.next = None

        self.triplets_arr: [Triplet] = []

    def triplet_add(self, triplet: Triplet) -> None:
        self.triplets_arr.append(triplet)

    def child_add_new(self) -> object:
        child = Graph()
        child.parent = self
        self.child = child
        return child

    def next_add_new(self) -> object:
        graph = Graph()
        graph.parent = self.parent
        self.next = graph
        graph.previous = self
        return graph

    def create_filter_condition_if_unexistant(self) -> None:
        if self.filter.is_condition_existant():
            return
        self.filter.create_condition()

    def set_filter_left_operand(self, left_operand: str) -> None:
        self.create_filter_condition_if_unexistant()
        self.filter.condition_temp.operand_left = left_operand

    def set_filter_operator(self, operator: str) -> None:
        self.create_filter_condition_if_unexistant()
        self.filter.condition_temp.operator = operator

    def set_filter_right_operand(self, right_operand: str) -> None:
        self.create_filter_condition_if_unexistant()
        self.filter.condition_temp.operand_right = right_operand

    def set_filter_negation(self, negation: bool) -> None:
        self.create_filter_condition_if_unexistant()
        self.filter.condition_temp.is_function_negated = negation

    def set_filter_function(self, function: str) -> None:
        self.create_filter_condition_if_unexistant()
        self.filter.condition_temp.function = function

    def set_filter_function_arguments(self, arguments: [str]) -> None:
        self.filter.condition_temp.arguments_arr = arguments

    def filter_condition_flush(self) -> None:
        self.create_filter_condition_if_unexistant()
        # not needed
        pass

    def filter_condition_create(self) -> None:
        self.filter.create_condition()

    def set_filter_logical_operator(self, logical_operator: str) -> None:
        self.filter.condition_temp.operator_logical_previous = logical_operator


def the_graph(graph) -> Graph:
    return graph
