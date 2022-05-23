from SPARQL.prefix import Prefix
from SPARQL.select import Select
from SPARQL.triplet import Triplet
from SPARQL.graph import Graph, the_graph
from SPARQL.order import Order


class Query:
    def __init__(self):
        self.prefixes_arr: [Prefix] = []
        self.name_map_prefix = dict()
        self.select = Select()
        self.order = Order()

        self.triplet_temp = Triplet()
        self.graphs_arr: [Graph] = []
        self.graph_temp = Graph()

        self.limit = -1
        self.offset = -1

    def prefix_add(self, name: str, prefix_str: str) -> None:
        prefix = Prefix(name, prefix_str)
        self.prefixes_arr.append(prefix)
        self.name_map_prefix[name] = prefix

    def set_distinct(self, is_distinct: bool) -> None:
        self.select.isDistinct = is_distinct

    def select_variable_add(self, variable: str) -> None:
        self.select.variable_add(variable)

    def triplet_set_subject(self, subject: str, datatype=None) -> None:
        self.triplet_temp.set_subject(subject, datatype)

    def triplet_set_predicate(self, predicate: str, datatype=None) -> None:
        self.triplet_temp.set_predicate(predicate, datatype)

    def triplet_set_object(self, the_object: str, datatype=None) -> None:
        self.triplet_temp.set_object(the_object, datatype)

    def triplet_flush_and_reset(self) -> None:
        if len(self.graphs_arr) == 0:
            self.graphs_arr.append(self.graph_temp)
        self.graph_temp.triplet_add(self.triplet_temp)
        self.triplet_temp = Triplet()

    def graph_child_add(self) -> None:
        # no root graph
        if len(self.graphs_arr) == 0:
            self.graphs_arr.append(self.graph_temp)
            return
        new_graph = the_graph(self.graph_temp.child_add_new())
        self.graphs_arr.append(new_graph)

    def graph_next_add(self) -> None:
        if len(self.graphs_arr) == 0:
            self.graphs_arr.append(self.graph_temp)
            return
        # new neighbor
        new_graph = the_graph(self.graph_temp.next_add_new())
        self.graphs_arr.append(new_graph)

    def graph_create_and_step_in(self) -> None:
        if len(self.graphs_arr) == 0:
            self.graphs_arr.append(self.graph_temp)
            return
        if self.graph_temp.child is None:
            self.graph_child_add()
            self.graph_temp = the_graph(self.graph_temp.child)
            return
        self.graph_temp = self.get_graph_youngest_child()
        self.graph_next_add()
        self.graph_temp = the_graph(self.graph_temp.next)

    def graph_step_out(self) -> None:
        if self.graph_temp.parent is None:
            raise Exception("Current graph has no place to step out")
        self.graph_temp = self.graph_temp.parent

    def get_graph_youngest_child(self) -> Graph:
        if self.graph_temp.child is None:
            raise Exception("Can not return youngest child of childest graph")
        child = the_graph(self.graph_temp.child)
        while child.next is not None:
            child = the_graph(child.next)
        return child

    def set_order(self, variables_arr: [str]) -> None:
        self.order.variables_arr = variables_arr

    def set_filter_left_operand(self, left_operand: str) -> None:
        self.graph_temp.set_filter_left_operand(left_operand)

    def set_filter_operator(self, operator: str) -> None:
        self.graph_temp.set_filter_operator(operator)

    def set_filter_right_operand(self, right_operand: str) -> None:
        self.graph_temp.set_filter_right_operand(right_operand)

    def set_filter_negation(self, negation: bool) -> None:
        self.graph_temp.set_filter_negation(negation)

    def set_filter_function(self, function: str) -> None:
        self.graph_temp.set_filter_function(function)

    def set_filter_function_arguments(self, arguments: [str]) -> None:
        self.graph_temp.set_filter_function_arguments(arguments)

    def filter_condition_flush(self) -> None:
        self.graph_temp.filter_condition_flush()

    def filter_condition_new(self, logical_operator: str) -> None:
        self.graph_temp.filter_condition_create()
        self.graph_temp.set_filter_logical_operator(logical_operator)

    # ----------- for normal usage

    def get_prefix_from_arr(self, index: int) -> Prefix:
        return self.prefixes_arr[index]

    def get_prefix_from_name_map(self, name: str) -> Prefix:
        return self.name_map_prefix[name]
